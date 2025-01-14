"""This module provides screen element detection and interaction functionality.

The module contains:
- Framework: Main class that coordinates screen analysis and interaction capabilities

Key features:
- Screenshot capture and processing
- Integration with ML models for element detection
- Conversion of predictions to interactive screen elements
- Label management and mapping
- Screen element interaction and automation
- Support for different operating modes (debug/capture)
- Device-agnostic model deployment
- Project configuration handling

The module serves as the main entry point for the screenwise framework,
orchestrating the detection and interaction with UI elements through:
- Automated testing and validation
- Screen element classification and analysis
- Coordinated interaction between predictions and user actions
- Flexible deployment across different environments and projects

This module integrates with other framework components to provide a complete
solution for screen analysis and automation tasks.
"""

import base64
import json

from PIL import ImageGrab
from t_screenwise.config import PATHS
from t_screenwise.models.screen_elements import ScreenElements, OCRElement
from t_screenwise.service import Service
from time import sleep, time


class Framework:
    """A framework for screen element detection and interaction.

    This class provides functionality for capturing screenshots, making predictions using
    a trained model, and converting predictions into interactive Box objects.

    Attributes:
        mode (str): Operating mode ('DEBUG' or 'CAPTURE'). Determines whether the framework
            uses provided image files ('DEBUG') or captures screenshots ('CAPTURE').
        model_name (str): Name of the model to use for predictions.
        service (Service): Service instance for handling API requests.
        labels_idx (dict[int, str]): Mapping of label indices to names, used for interpreting
            model predictions.
        labels_name (dict[str, int]): Mapping of label names to indices, used for filtering
            predictions.
        OCR_URL (str): URL for the OCR service endpoint.
        PREDICTOR_URL (str): URL for the predictor service endpoint.
    """

    def __init__(self, model_name: str, service: Service, mode: str = "CAPTURE", labels: str = "") -> None:
        """Initialize the Framework.

        Args:
            model_name (str): Name of the model to use for predictions.
            service (Service): Service instance for handling API requests.
            mode (str, optional): Operating mode for the framework. Can be either 'DEBUG' or 'CAPTURE'.
                'DEBUG' mode uses provided image files while 'CAPTURE' takes screenshots. Defaults to "CAPTURE".
            labels (str, optional): Path to JSON file containing label name to index mappings. Defaults to "".
        """
        self.mode = mode
        self.model_name = model_name
        self.service = service
        self.get_urls(self.service)
        self.set_labels(labels)

    def get_urls(self, service: Service) -> None:
        """Set the OCR and Predictor service URLs.

        This method iterates over the endpoints provided by the service and assigns
        the appropriate URL to either the OCR or Predictor URL attributes based on
        the presence of the substring 'ocr' in the endpoint.

        Args:
            service (Service): The service instance containing the base URL and endpoints.
        """
        for endpoint in self.service.endpoints:
            if "ocr" in endpoint:
                self.OCR_URL = endpoint
            else:
                self.PREDICTOR_URL = endpoint

    def set_labels(self, labels: str) -> None:
        """Load and set up label mappings from a JSON file.

        Args:
            labels (str): Path to labels JSON file
        """
        with open(labels, "r") as f:
            labels_dict = json.load(f)
        self.labels_idx = {v: k for k, v in labels_dict.items()}
        self.labels_name = {k: v for k, v in labels_dict.items()}

    def get_screenshot(self, filename: str = None) -> str:
        """Capture and save a screenshot.

        Args:
            filename (str, optional): Path to save screenshot. Defaults to None.

        Returns:
            str: Path where screenshot was saved
        """
        file_name = filename if filename else PATHS.TEMP / "screenshot.png"
        snapshot = ImageGrab.grab()
        snapshot.save(file_name)
        return file_name

    def get_image(self, filename: str) -> str:
        """Get image path based on mode.

        Args:
            filename (str): Path to image file

        Returns:
            str: Path to image to use
        """
        if self.mode == "CAPTURE":
            file_name = self.get_screenshot()
        elif self.mode == "DEBUG":
            file_name = filename

        return file_name

    def prediction_to_boxes(self, image: str, filter: list = None, unique: bool = True) -> list:
        """Convert model predictions to Box objects.

        Args:
            image (str): Path to source image
            unique (bool, optional): Whether to ensure unique detections. Defaults to True.

        Returns:
            list: List of Box objects created from predictions
        """
        encoded_image = self.encode_image(image)
        predictions = self.service.make_api_request(
            self.PREDICTOR_URL,
            method="post",
            json={
                "image": encoded_image,
                "unique": unique,
                "model_request": {"model_name": self.model_name, "filters": filter},
            },
        )
        boxes_list = []

        if len(predictions["elements"]) > 0:
            # Iterate over the predictions and create elements using ScreenElements
            for prediction in predictions["elements"]:
                coords = [prediction["x1"], prediction["y1"], prediction["x2"], prediction["y2"]]
                label = prediction["label"]
                score = prediction["score"]

                box = ScreenElements(
                    x1=coords[0],
                    y1=coords[1],
                    x2=coords[2],
                    y2=coords[3],
                    label=label,
                    score=score,
                    image_path=image,
                    mode=self.mode,
                )
                boxes_list.append(box)

        return boxes_list

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 string.

        Args:
            image_path (str): Path to image file

        Returns:
            str: Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def get_ocr_elements(self, image_path: str, filter: list[str] = [], unique: bool = True) -> list[OCRElement]:
        """Process image with EasyOCR and return OCRElement objects.

        Args:
            image_path (str): Path to image file
            filter (list[str], optional): List of text strings to filter for. Defaults to None.

        Returns:
            list[OCRElement]: List of OCRElement objects containing detected text
        """
        image_encoded = self.encode_image(image_path)
        results = self.service.make_api_request(
            self.OCR_URL, method="post", json={"image": image_encoded, "filters": filter, "unique": unique}
        )

        ocr_elements = []
        text_elements = results.get("elements", None)
        if text_elements:
            for result in text_elements:  # [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                text = result["text"]
                confidence = result["confidence"]

                # Convert bbox to x1,y1,x2,y2 format
                x1 = result["x1"]
                y1 = result["y1"]
                x2 = result["x2"]
                y2 = result["y2"]

                ocr_element = OCRElement(text=text, confidence=confidence, x1=x1, y1=y1, x2=x2, y2=y2)
                ocr_elements.append(ocr_element)
        self.ocr_results = ocr_elements

        if filter:
            filtered_elements = []
            for text in filter:
                matches = OCRElement.find_by_text(ocr_elements, text, partial_match=True)
                filtered_elements.extend(matches)
            return filtered_elements

        return ocr_elements

    def get(self, filter: list[str] = None, image: str = None, unique: bool = True, process_ocr: bool = False) -> list:
        """Get detected boxes and optionally OCR elements from an image.

        Args:
            filter (list[str], optional): Labels to filter for. Defaults to None.
            image (str, optional): Path to image file. Defaults to None.
            unique (bool, optional): Whether to ensure unique detections. Defaults to True.
            process_ocr (bool, optional): Whether to process OCR for text elements. Defaults to False.

        Returns:
            list: List of detected Box objects and OCRElement objects if process_ocr=True
        """
        file_name = self.get_image(image)

        ocr_filter = []
        model_filter = []
        # Get standard predictions
        if filter:
            for label in filter:
                if label not in self.labels_name and process_ocr:
                    ocr_filter.append(label)
                else:
                    model_filter.append(self.labels_name[label] if label in self.labels_name else label)
            filter = model_filter
        boxes = []
        if not process_ocr:
            boxes = self.prediction_to_boxes(file_name, model_filter, unique)
        else:
            ocr_elements = self.get_ocr_elements(file_name, ocr_filter, unique)
            boxes.extend(ocr_elements)

        return boxes if len(boxes) > 1 else boxes[0] if boxes else None

    def wait_for_element(self, element: str, image: str = None, timeout: int = 10) -> list | None:
        """Wait for an element to appear on the screen.

        Repeatedly checks for the presence of a specified element by name until it is found
        or the timeout is reached.

        Args:
            element (str): The name of the element to wait for
            image (str, optional): Path to image file to check. If None, captures screenshot. Defaults to None.
            timeout (int, optional): Maximum time in seconds to wait. Defaults to 10.

        Returns:
            list | None: List of detected Box objects if element found, None if timeout reached
        """
        condition = False
        start_time = time()
        timeout_reached = False
        visible = False

        while not condition:
            boxes = self.get(filter=[element], image=image)
            if time() - start_time > timeout:
                timeout_reached = True
            if boxes:
                visible = True

            sleep(1)
            if timeout_reached or visible:
                condition = True

        return boxes
