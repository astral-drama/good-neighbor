"""A project that manages custom widgets for the purpose of creating a default homepage in your web browser."""

__version__ = "0.1.0"
__author__ = "Seth Lakowske"
__email__ = "lakowske@gmail.com"

from .actions.build import build
from .core import calculate_sum, greet

__all__ = ["greet", "calculate_sum", "build"]
