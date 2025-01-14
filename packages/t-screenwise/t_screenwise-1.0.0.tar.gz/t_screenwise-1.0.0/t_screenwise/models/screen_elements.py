"""This module provides unified screen element handling functionality.

The module contains classes for detecting, analyzing and interacting with UI elements:

- Margin: Helper class for calculating margins as percentages of element dimensions
- ScreenElement: Base class that combines grid-based positioning and bounding box functionality
  for UI elements, with methods for coordinate calculations, drawing, and interaction
- OCRElement: Extension of ScreenElement that adds OCR-specific capabilities like text content,
  confidence scores, and spatial relationship analysis between text elements

Key features:
- Flexible margin calculations based on element dimensions
- Grid-based coordinate system for precise element positioning
- Drawing capabilities for visualization and debugging
- Mouse and keyboard interaction methods
- OCR text detection with confidence scoring
- Spatial relationship analysis between elements
- Support for both pixel and percentage-based measurements

This module serves as the foundation for screen element handling in the framework,
enabling consistent detection, positioning and interaction across different element types.
"""

from dataclasses import dataclass, field
from PIL import Image, ImageColor, ImageDraw
from typing import Optional, Union, Dict, List, Tuple
import random
from pyautogui import click as cl
from pyautogui import write as sk
from pyautogui import press as prss


class Margin:
    """A class that calculates margin sizes based on a percentage of dimensions.

    This class is used to calculate margins for a grid or box, where the margins
    are defined as a percentage of the total height and width.

    Attributes:
        height (float): The total height to calculate margins from
        width (float): The total width to calculate margins from
        percent (float): The percentage to use for margin calculations
    """

    def __init__(self, height: float, width: float, percent: float) -> None:
        """Initialize the Margin with dimensions and percentage.

        Args:
            height (float): The total height
            width (float): The total width
            percent (float): The percentage to use for margins (e.g. 10 for 10%)
        """
        self.height = height
        self.width = width
        self.percent = percent

    def percentage(self, number: float) -> float:
        """Calculate a percentage of a number.

        Args:
            number (float): The number to calculate percentage of

        Returns:
            float: The calculated percentage value
        """
        return (self.percent / 100) * number

    def top(self) -> float:
        """Calculate the top margin.

        Returns:
            float: The top margin size as percentage of height
        """
        return self.percentage(self.height)

    def bottom(self) -> float:
        """Calculate the bottom margin.

        Returns:
            float: The bottom margin size as percentage of height
        """
        return self.percentage(self.height)

    def left(self) -> float:
        """Calculate the left margin.

        Returns:
            float: The left margin size as percentage of width
        """
        return self.percentage(self.width)

    def right(self) -> float:
        """Calculate the right margin.

        Returns:
            float: The right margin size as percentage of width
        """
        return self.percentage(self.width)


@dataclass
class ScreenElements:
    """Base class for screen elements combining Grid and Box functionality.

    This class provides core functionality for handling screen elements including
    coordinate calculations, drawing capabilities, and interaction methods.

    Attributes:
        x1 (float): Left x-coordinate
        y1 (float): Top y-coordinate
        x2 (float): Right x-coordinate
        y2 (float): Bottom y-coordinate
        label (str): Label describing the element
        score (float): Confidence score for the element
        image_path (str): Path to image file for drawing
        mode (str): Operating mode ('DEBUG' or 'CAPTURE')
        image (Optional[Image.Image]): PIL Image object for drawing
        draw (Optional[ImageDraw.ImageDraw]): Drawing interface
        color (Tuple[int, int, int]): RGB color tuple for drawing
        COORDS (Dict[str, Tuple[float, float]]): Named coordinate positions
    """

    x1: float
    y1: float
    x2: float
    y2: float
    label: str = ""
    score: float = 0.0
    image_path: str = ""
    mode: str = "CAPTURE"

    # Initialize optional attributes with default factory
    image: Optional[Image.Image] = field(default=None, init=False)
    draw: Optional[ImageDraw.ImageDraw] = field(default=None, init=False)
    color: Tuple[int, int, int] = field(default_factory=lambda: (0, 0, 0), init=False)
    COORDS: Dict[str, Tuple[float, float]] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """Initialize additional attributes after dataclass initialization."""
        self.margin = Margin(self.height, self.width, 10)
        self.color = self._get_random_color()
        self.COORDS = self.generate_coords()

        if self.image_path:
            self.image = Image.open(self.image_path)
            self.draw = ImageDraw.Draw(self.image)

    def generate_coords(self) -> Dict[str, Tuple[float, float]]:
        """Generate a dictionary of named coordinate positions.

        Returns:
            Dict[str, Tuple[float, float]]: Mapping of position names to (x,y) coordinates
        """
        return {
            "default": self.middle(),
            "up": self.up(),
            "down": self.down(),
            "left": self.left(),
            "right": self.right(),
            "up_right": self.up_right(),
            "up_left": self.up_left(),
            "down_left": self.down_left(),
            "down_right": self.down_right(),
            "middle": self.middle(),
        }

    def resolve_coords(self, coords: Union[str, Tuple[float, float]]) -> Tuple[float, float]:
        """Resolve the coordinates based on the given key or direct value.

        Args:
            coords (Union[str, Tuple[float, float]]): Named position or explicit coordinates

        Returns:
            Tuple[float, float]: The resolved (x,y) coordinates
        """
        if isinstance(coords, str):
            return self.COORDS.get(coords, self.middle())
        return coords

    def draw_point_text(self, coords: Tuple[float, float], text: Optional[str] = None, align: str = "left") -> None:
        """Draw point and optional text at specified coordinates.

        Args:
            coords (Tuple[float, float]): (x,y) coordinates to draw at
            text (Optional[str]): Text to draw (defaults to element label if None)
            align (str): Text alignment ('left', 'right', or 'center')
        """
        if not self.draw:
            return

        text = text or self.label
        x, y = coords
        r = 3
        self.draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=self.color)
        self.draw.point((x, y), fill="black")
        self.draw.text((x, y), text, fill="black", align=align)

    def handle_debug(self, coords: Tuple[float, float], keys: Optional[str] = None) -> None:
        """Handle debug mode logic by drawing on the image.

        Args:
            coords (Tuple[float, float]): (x,y) coordinates to draw at
            keys (Optional[str]): Optional keyboard input to display
        """
        if not self.image:
            return

        self.draw_point_text(coords)
        if keys:
            self.draw.text(self.right(), keys, fill="black")
        self.image.show()

    def click(self, coords: Union[str, Tuple[float, float]] = "default", button: str = "left", clicks: int = 1) -> None:
        """Perform a mouse click at specified coordinates.

        Args:
            coords (Union[str, Tuple[float, float]]): Named position or explicit coordinates
            button (str): Mouse button to click ('left' or 'right')
            clicks (int): Number of clicks to perform
        """
        resolved_coords = self.resolve_coords(coords)
        if self.mode == "DEBUG":
            self.handle_debug(resolved_coords)
        else:
            cl(x=resolved_coords[0], y=resolved_coords[1], clicks=clicks, button=button)

    def send_keys(self, keys: str) -> None:
        """Send keyboard input.

        Args:
            keys (str): Text to type
        """
        if self.mode != "DEBUG":
            sk(keys)

    def click_and_send_keys(
        self, keys: str, coords: Union[str, Tuple[float, float]] = "default", button: str = "left"
    ) -> None:
        """Perform a click followed by keyboard input.

        Args:
            keys (str): Text to type after clicking
            coords (Union[str, Tuple[float, float]]): Named position or explicit coordinates
            button (str): Mouse button to click ('left' or 'right')
        """
        resolved_coords = self.resolve_coords(coords)
        if self.mode == "DEBUG":
            self.handle_debug(resolved_coords, keys)
        else:
            self.click(coords=resolved_coords, button=button)
            self.send_keys(keys)

    def press(self, keys: str) -> None:
        """Press a keyboard key.

        Args:
            keys (str): The key or key combination to press (e.g. 'enter', 'ctrl+c')

        Note:
            In DEBUG mode, this method will not perform any keyboard actions.
            In normal mode, it uses pyautogui to simulate the key press.
        """
        if self.mode != "DEBUG":
            prss(keys)

    @property
    def width(self) -> float:
        """Calculate the width of the element.

        Returns:
            float: Width in pixels
        """
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        """Calculate the height of the element.

        Returns:
            float: Height in pixels
        """
        return self.y2 - self.y1

    def middle(self) -> tuple[float, float]:
        """Calculate the center point of the grid.

        Returns:
            tuple[float, float]: (x,y) coordinates of the center point
        """
        return (self.width / 2) + self.x1, (self.height / 2) + self.y1

    def right(self) -> tuple[float, float]:
        """Calculate the middle-right point with margin.

        Returns:
            tuple[float, float]: (x,y) coordinates of the middle-right point
        """
        return self.x2 - self.margin.right(), self.y2 - (self.height / 2)

    def left(self) -> tuple[float, float]:
        """Calculate the middle-left point with margin.

        Returns:
            tuple[float, float]: (x,y) coordinates of the middle-left point
        """
        return self.x1 + self.margin.left(), self.y1 + (self.height / 2)

    def up(self) -> tuple[float, float]:
        """Calculate the top-middle point with margin.

        Returns:
            tuple[float, float]: (x,y) coordinates of the top-middle point
        """
        return (self.width / 2) + self.x1, self.y1 + self.margin.top()

    def down(self) -> tuple[float, float]:
        """Calculate the bottom-middle point with margin.

        Returns:
            tuple[float, float]: (x,y) coordinates of the bottom-middle point
        """
        return (self.width / 2) + self.x1, self.y2 - self.margin.bottom()

    def up_right(self) -> tuple[float, float]:
        """Calculate the top-right point with margins.

        Returns:
            tuple[float, float]: (x,y) coordinates of the top-right point
        """
        return self.x2 - self.margin.right(), self.y1 + self.margin.top()

    def down_right(self) -> tuple[float, float]:
        """Calculate the bottom-right point with margins.

        Returns:
            tuple[float, float]: (x,y) coordinates of the bottom-right point
        """
        return self.x2 - self.margin.right(), self.y2 - self.margin.bottom()

    def up_left(self) -> tuple[float, float]:
        """Calculate the top-left point with margins.

        Returns:
            tuple[float, float]: (x,y) coordinates of the top-left point
        """
        return self.x1 + self.margin.left(), self.y1 + self.margin.top()

    def down_left(self) -> tuple[float, float]:
        """Calculate the bottom-left point with margins.

        Returns:
            tuple[float, float]: (x,y) coordinates of the bottom-left point
        """
        return self.x1 + self.margin.left(), self.y2 - self.margin.bottom()

    def all(self) -> dict[str, tuple[float, float]]:
        """Get all grid points with margins.

        Returns:
            dict[str, tuple[float, float]]: Dictionary mapping position names to their (x,y) coordinates
        """
        response = {
            "left": self.left(),
            "down_left": self.down_left(),
            "up_left": self.up_left(),
            "right": self.right(),
            "down_right": self.down_right(),
            "up_right": self.up_right(),
            "down": self.down(),
            "middle": self.middle(),
            "up": self.up(),
        }
        return response

    def draw_all(self) -> None:
        """Draw all coordinate points with their labels on the image."""
        for counter, (key, value) in enumerate(self.all().items()):
            align = "left" if counter < 3 else "right" if counter < 6 else "center"
            self.draw_point_text(value, key, align=align)
        self.image.show()

    def _get_random_color(self) -> Tuple[int, int, int]:
        """Generate a random RGB color tuple.

        Returns:
            Tuple[int, int, int]: Random RGB color values
        """
        return ImageColor.getrgb(f"#{random.randint(0, 0xFFFFFF):06X}")


class OCRElement(ScreenElements):
    """Extension of ScreenElement with OCR-specific functionality.

    This class adds OCR-specific features like text content, confidence scores,
    and spatial relationship analysis between text elements.

    Attributes:
        text (str): The detected text content
        confidence (float): Confidence score of the text detection
    """

    def __init__(self, text: str, confidence: float, x1: int, y1: int, x2: int, y2: int):
        """Initialize OCRElement with text and position data.

        Args:
            text (str): The detected text content
            confidence (float): Confidence score of the detection
            x1 (int): Left x-coordinate
            y1 (int): Top y-coordinate
            x2 (int): Right x-coordinate
            y2 (int): Bottom y-coordinate
        """
        super().__init__(x1=x1, y1=y1, x2=x2, y2=y2, label=text, score=confidence)
        self.text = text
        self.confidence = confidence

    def _find_nearest_in_direction(
        self, detections: List["OCRElement"], direction: str, n: int = 1
    ) -> List["OCRElement"]:
        """Helper method to find n nearest boxes in a given direction.

        Args:
            detections (List['OCRElement']): List of OCR elements to search through
            direction (str): Direction to search ('right', 'left', 'above', 'below')
            n (int): Number of nearest elements to return

        Returns:
            List['OCRElement']: List of n nearest OCR elements in the specified direction
        """
        candidates = []

        for detection in detections:
            if detection == self:
                continue

            if direction == "right" and detection.x1 > self.x2:
                # Check vertical overlap
                if not (detection.y2 < self.y1 or detection.y1 > self.y2):
                    distance = detection.x1 - self.x2
                    candidates.append((distance, detection))

            elif direction == "left" and detection.x2 < self.x1:
                # Check vertical overlap
                if not (detection.y2 < self.y1 or detection.y1 > self.y2):
                    distance = self.x1 - detection.x2
                    candidates.append((distance, detection))

            elif direction == "above" and detection.y2 < self.y1:
                # Check horizontal overlap
                if not (detection.x2 < self.x1 or detection.x1 > self.x2):
                    distance = self.y1 - detection.y2
                    candidates.append((distance, detection))

            elif direction == "below" and detection.y1 > self.y2:
                # Check horizontal overlap
                if not (detection.x2 < self.x1 or detection.x1 > self.x2):
                    distance = detection.y1 - self.y2
                    candidates.append((distance, detection))

        # Sort by distance and return n nearest
        candidates.sort(key=lambda x: x[0])
        return [detection for _, detection in candidates[:n]]

    def get_nearest_boxes(self, detections: List["OCRElement"], n: int = 1) -> Dict[str, List["OCRElement"]]:
        """Get the n nearest boxes in all directions.

        Args:
            detections (List['OCRElement']): List of all OCR objects
            n (int): Number of nearest boxes to return in each direction (default: 1)

        Returns:
            Dict[str, List['OCRElement']]: Dictionary with lists of nearest boxes in each direction
        """
        return {
            "right": self._find_nearest_in_direction(detections, "right", n),
            "left": self._find_nearest_in_direction(detections, "left", n),
            "above": self._find_nearest_in_direction(detections, "above", n),
            "below": self._find_nearest_in_direction(detections, "below", n),
        }

    @staticmethod
    def find_by_text(
        detections: List["OCRElement"], search_text: str, partial_match: bool = False
    ) -> List["OCRElement"]:
        """Find OCR detections by text.

        Args:
            detections (List['OCRElement']): List of OCR objects to search through
            search_text (str): Text to search for
            partial_match (bool): If True, returns partial matches. If False, requires exact match

        Returns:
            List['OCRElement']: List of matching OCR objects
        """
        matches = []
        search_text = search_text.lower()

        for detection in detections:
            detected_text = detection.text.lower()
            if partial_match and search_text in detected_text:
                matches.append(detection)
            elif detected_text == search_text:
                matches.append(detection)

        return matches
