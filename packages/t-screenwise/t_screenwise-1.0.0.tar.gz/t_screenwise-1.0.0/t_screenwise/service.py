"""Service module for handling API interactions.

This module provides the Service class which handles:
- API endpoint discovery through OpenAPI specification
- Schema resolution and validation
- Request handling with retry logic
- Cold start management
"""

import json
import requests
from time import sleep
from retry import retry
from requests.exceptions import ConnectionError
from t_screenwise.utils.logger import logger


class ServerError(Exception):
    """Custom exception for server-side errors."""

    pass


class Service:
    """Handles API service URLs and requests.

    This class manages the base URL for the service and provides methods for making API requests.
    It automatically parses the OpenAPI specification to discover available endpoints.

    Attributes:
        base_url (str): Base URL for the service
        endpoints (dict): Dictionary of available endpoints parsed from OpenAPI spec
    """

    def __init__(self, base_url: str):
        """Initialize the Service.

        Args:
            base_url (str): Base URL for the service
        """
        self.base_url = base_url
        self.endpoints = {}
        self._initialize_endpoints()

    def _wait_for_cold_start(self, max_retries: int = 20, delay: int = 10, backoff: int = 5) -> bool:
        """Wait for the service to be available during cold start.

        Args:
            max_retries (int): Maximum number of retry attempts. Defaults to 20.
            delay (int): Initial delay between retries in seconds. Defaults to 10.
            backoff (int): Additional delay to add after each retry. Defaults to 5.

        Returns:
            bool: True if service becomes available, False if max retries exceeded

        Raises:
            ConnectionError: If service does not become available within max retries
        """
        attempt = 0
        current_delay = delay

        while attempt < max_retries:
            try:
                openapi_url = f"{self.base_url}/openapi.json"
                logger.info(f"Cold start check attempt {attempt + 1}/{max_retries}")
                response = requests.get(openapi_url)
                if response.status_code == 200:
                    logger.info("Service is available")
                    return True
            except requests.exceptions.RequestException:
                pass

            attempt += 1
            sleep(current_delay)
            current_delay += backoff

        error_msg = f"Service not available after {max_retries} attempts"
        logger.error(error_msg)
        raise ConnectionError(error_msg)

    @retry((ConnectionError, ServerError), tries=3, delay=3)
    def _initialize_endpoints(self):
        """Query the base URL for OpenAPI spec and initialize endpoints."""
        try:
            # Wait for service to be available
            self._wait_for_cold_start()

            # Now get and parse the OpenAPI spec
            openapi_url = f"{self.base_url}/openapi.json"
            response = requests.get(openapi_url)
            response.raise_for_status()
            self.endpoints = self._parse_openapi_endpoints(response.json())
            logger.info("Successfully initialized endpoints")
            logger.info("You can get the endpoints by calling the 'endpoints' attribute")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to initialize endpoints: {str(e)}")
            raise ConnectionError(f"Failed to connect to the API: {str(e)}") from e

    def _parse_openapi_endpoints(self, response_json: dict) -> dict:
        """Parse OpenAPI JSON response into a dictionary of endpoints.

        Args:
            response_json (dict): OpenAPI specification JSON

        Returns:
            dict: Dictionary of endpoints with their HTTP methods and details
        """
        self._schemas = response_json.get("components", {}).get("schemas", {})
        endpoints = {}

        for path, methods in response_json.get("paths", {}).items():
            endpoints[path] = {}
            for method, details in methods.items():
                endpoints[path][method] = {
                    "summary": details.get("summary"),
                    "operationId": details.get("operationId"),
                    "requestSchema": details.get("requestBody", {})
                    .get("content", {})
                    .get("application/json", {})
                    .get("schema", {}),
                    "responseSchema": details.get("responses", {})
                    .get("200", {})
                    .get("content", {})
                    .get("application/json", {})
                    .get("schema", {}),
                }

        return endpoints

    def _resolve_schema(self, schema: dict) -> dict:
        """Resolve a schema by following its references recursively.

        Args:
            schema (dict): Schema object that may contain references

        Returns:
            dict: Resolved schema with all references replaced with actual definitions
        """
        if not schema:
            return {}

        # If it's a direct reference, resolve it
        if "$ref" in schema:
            ref = schema["$ref"]
            if ref.startswith("#/components/schemas/"):
                schema_name = ref.split("/")[-1]
                if schema_name in self._schemas:
                    return self._resolve_schema(self._schemas[schema_name])
                else:
                    logger.warning(f"Schema reference {schema_name} not found")
                    return {}

        # Create a copy to avoid modifying the original
        resolved = schema.copy()

        # Resolve nested references in properties
        if "properties" in schema:
            resolved["properties"] = {}
            for prop_name, prop_schema in schema["properties"].items():
                if isinstance(prop_schema, dict):
                    if "$ref" in prop_schema:
                        resolved["properties"][prop_name] = self._resolve_schema(prop_schema)
                    else:
                        # Handle arrays with items that might have refs
                        if prop_schema.get("type") == "array" and "items" in prop_schema:
                            items = prop_schema["items"]
                            if isinstance(items, dict) and "$ref" in items:
                                prop_schema["items"] = self._resolve_schema(items)
                        resolved["properties"][prop_name] = prop_schema

        # Include other schema attributes
        for key in ["type", "required", "title", "description", "enum", "const"]:
            if key in schema:
                resolved[key] = schema[key]

        return resolved

    def get_endpoint_schemas(self, endpoint: str, method: str = "post") -> dict:
        """Get the request and response schemas for a specific endpoint.

        Args:
            endpoint (str): The endpoint path
            method (str, optional): HTTP method. Defaults to "post".

        Returns:
            dict: Dictionary containing request and response schemas

        Raises:
            ValueError: If endpoint or method not found
        """
        if endpoint not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint}")

        if method not in self.endpoints[endpoint]:
            raise ValueError(f"Method {method} not available for endpoint {endpoint}")

        endpoint_info = self.endpoints[endpoint][method]

        schemas = {
            "request": self._resolve_schema(endpoint_info["requestSchema"]),
            "response": self._resolve_schema(endpoint_info["responseSchema"]),
            "summary": endpoint_info["summary"],
            "operationId": endpoint_info["operationId"],
        }

        # Log the resolved schemas for debugging
        logger.debug(f"Resolved schemas for {endpoint} {method}:")
        logger.debug(f"Request schema: {schemas['request']}")
        logger.debug(f"Response schema: {schemas['response']}")

        return schemas

    @retry((ConnectionError, ServerError), tries=3, delay=3)
    def make_api_request(self, endpoint: str, method: str = "post", **kwargs) -> dict:
        """Make API request to a specific endpoint.

        Args:
            endpoint (str): The endpoint path to call
            method (str, optional): HTTP method to use. Defaults to "post".
            **kwargs: Additional arguments to pass to the request

        Returns:
            dict: API response data

        Raises:
            ServerError: If the server returns a 500 error
            ValueError: If there are validation errors in the request
        """
        if endpoint not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint}")

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            logger.info(f"Sending {method} request to {endpoint}")
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 500:
                error_message = f"Server error occurred: {response.text}"
                raise ServerError(error_message) from e
            elif response.status_code == 422:
                try:
                    error_detail = response.json().get("detail", [])
                    error_messages = []
                    for error in error_detail:
                        field = " -> ".join(str(loc) for loc in error["loc"])
                        message = f"Field '{field}': {error['msg']}"
                        error_messages.append(message)

                    raise ValueError("Validation error in API request:\n" + "\n".join(error_messages)) from e
                except json.JSONDecodeError:
                    raise ValueError(f"Invalid response from API: {response.text}") from e
            else:
                raise ValueError(f"API request failed with status code {response.status_code}: {response.text}") from e
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to the API: {str(e)}") from e
