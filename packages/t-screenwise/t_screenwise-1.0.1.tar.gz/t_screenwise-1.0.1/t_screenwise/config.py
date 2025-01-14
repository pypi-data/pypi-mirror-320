"""Configuration file for the training setup."""

import os
import tempfile
from pathlib import Path


class Paths:
    """Class containing path configurations."""

    def __init__(self):
        """Initialize paths."""
        self.TEMP = Path(tempfile.gettempdir()) / "screenwise"
        # Create temp directory if it doesn't exist
        os.makedirs(self.TEMP, exist_ok=True)


PATHS = Paths()

OCR_URL = os.getenv("OCR_URL")
PREDICTOR_URL = os.getenv("PREDICTOR_URL")
