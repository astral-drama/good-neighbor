"""Effect types for composable, testable code.

This module provides algebraic effect types following category theory principles:
- IO[A]: Monad for suspended side effects
- Result[E, A]: Monad for error handling (Success | Failure)
- ErrorDetails: Structured error information
"""

from .error_details import ErrorDetails
from .io import IO, Effect, FlatMapped, Pure
from .result import Failure, Result, Success

__all__ = [
    "IO",
    "Pure",
    "Effect",
    "FlatMapped",
    "Result",
    "Success",
    "Failure",
    "ErrorDetails",
]
