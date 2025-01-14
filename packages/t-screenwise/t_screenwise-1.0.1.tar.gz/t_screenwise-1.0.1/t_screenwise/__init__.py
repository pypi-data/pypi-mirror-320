"""Top-level package for t-screenwise."""

__author__ = """Nikolas Cohn, Alejandro Muñoz"""
__email__ = "support@thoughtful.ai"
__version__ = "1.0.1"

from .screenwise import Framework
from .service import Service

__all__ = [
    "Framework",
    "Service",
]
