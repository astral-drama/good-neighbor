"""Structured error information for Result monad."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ErrorDetails:
    """Algebraic error type for Result monad.

    Provides structured error information with:
    - code: Machine-readable error code (e.g., "NOT_FOUND", "VALIDATION_ERROR")
    - message: Human-readable error message
    - details: Additional context-specific error information
    """

    code: str
    message: str
    details: dict = field(default_factory=dict)

    def __str__(self) -> str:
        """Return human-readable error representation."""
        if self.details:
            return f"{self.code}: {self.message} (details: {self.details})"
        return f"{self.code}: {self.message}"
