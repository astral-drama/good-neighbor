"""Result monad for algebraic error handling.

Result[E, A] = Success[A] | Failure[E]

This is a sum type (algebraic data type) representing either success or failure.
It follows the Functor and Monad laws.
"""

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar, Union, cast

E = TypeVar("E")
A = TypeVar("A")
B = TypeVar("B")


@dataclass(frozen=True)
class Success(Generic[A]):
    """Successful computation with a value.

    Functor laws:
    - Identity: Success(x).map(lambda a: a) == Success(x)
    - Composition: Success(x).map(f).map(g) == Success(x).map(lambda a: g(f(a)))

    Monad laws:
    - Left identity: Success(x).flat_map(f) == f(x)
    - Right identity: Success(x).flat_map(Success) == Success(x)
    - Associativity: Success(x).flat_map(f).flat_map(g) ==
                     Success(x).flat_map(lambda a: f(a).flat_map(g))
    """

    value: A

    def map(self, f: Callable[[A], B]) -> "Result[E, B]":
        """Functor map: transform the success value.

        Args:
            f: Function to apply to the success value

        Returns:
            Success with transformed value
        """
        return Success(f(self.value))  # type: ignore[arg-type]

    def flat_map(self, f: Callable[[A], "Result[E, B]"]) -> "Result[E, B]":
        """Monadic bind: chain computations that may fail.

        Args:
            f: Function that returns a Result

        Returns:
            Result from applying f to the success value
        """
        return f(self.value)

    def map_error(self, f: Callable[[E], E]) -> "Result[E, A]":
        """Map over the error (no-op for Success).

        Args:
            f: Function to transform error (unused)

        Returns:
            Unchanged Success
        """
        return cast("Result[E, A]", self)

    def is_success(self) -> bool:
        """Check if this is a Success."""
        return True

    def is_failure(self) -> bool:
        """Check if this is a Failure."""
        return False


@dataclass(frozen=True)
class Failure(Generic[E]):
    """Failed computation with an error.

    Functor laws hold (Failure propagates unchanged).
    Monad laws hold (Failure short-circuits).
    """

    error: E

    def map(self, f: Callable[[A], B]) -> "Result[E, B]":
        """Functor map: propagate failure unchanged.

        Args:
            f: Function to apply (unused)

        Returns:
            Unchanged Failure
        """
        # Cast is safe: Failure[E] is valid for any Result[E, X]
        return cast(Result[E, B], self)

    def flat_map(self, f: Callable[[A], "Result[E, B]"]) -> "Result[E, B]":
        """Monadic bind: propagate failure unchanged.

        Args:
            f: Function that returns a Result (unused)

        Returns:
            Unchanged Failure
        """
        return cast(Result[E, B], self)

    def map_error(self, f: Callable[[E], E]) -> "Result[E, A]":
        """Map over the error.

        Args:
            f: Function to transform error

        Returns:
            Failure with transformed error
        """
        return cast(Result[E, A], Failure(f(self.error)))

    def is_success(self) -> bool:
        """Check if this is a Success."""
        return False

    def is_failure(self) -> bool:
        """Check if this is a Failure."""
        return True


# Type alias for the sum type
Result = Union[Success[A], Failure[E]]


def success(value: A) -> Result[E, A]:
    """Create a Success result.

    Args:
        value: The success value

    Returns:
        Success containing the value
    """
    return Success(value)  # type: ignore[arg-type]


def failure(error: E) -> Result[E, A]:
    """Create a Failure result.

    Args:
        error: The error

    Returns:
        Failure containing the error
    """
    return Failure(error)  # type: ignore[arg-type]
