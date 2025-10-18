"""IO monad for suspended side effects.

IO[A] represents a suspended computation that produces A when executed.
Side effects are not executed until .run() is called, enabling:
- Composability: Chain operations without executing them
- Testability: Inspect computation structure without running side effects
- Referential transparency: IO values are immutable descriptions of effects
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

A_co = TypeVar("A_co", covariant=True)
B = TypeVar("B")


class IO(Generic[A_co], ABC):
    """IO[A] monad for suspended side effects.

    Functor laws:
    - Identity: io.map(lambda x: x) == io
    - Composition: io.map(f).map(g) == io.map(lambda x: g(f(x)))

    Monad laws:
    - Left identity: Pure(a).flat_map(f) == f(a)
    - Right identity: io.flat_map(Pure) == io
    - Associativity: io.flat_map(f).flat_map(g) ==
                     io.flat_map(lambda x: f(x).flat_map(g))

    The laws are verified by property-based tests.
    """

    @abstractmethod
    def run(self) -> A_co:
        """Execute the side effect and return the result.

        This is the only method that actually performs side effects.
        All other methods (map, flat_map) build up a computation structure
        without executing anything.

        Returns:
            The result of executing the computation
        """

    def map(self, f: Callable[[A_co], B]) -> IO[B]:
        r"""Functor map: transform the result of this IO.

        Args:
            f: Function to apply to the result

        Returns:
            New IO that applies f to the result when run

        Example:
            >>> read_file = Effect(lambda: open("data.txt").read())
            >>> line_count = read_file.map(lambda content: len(content.split("\n")))
            >>> line_count.run()  # Returns number of lines
        """
        return FlatMapped(self, lambda a: Pure(f(a)))  # type: ignore[arg-type]

    def flat_map(self, f: Callable[[A_co], IO[B]]) -> IO[B]:
        """Monadic bind: chain IO computations.

        Args:
            f: Function that takes the result and returns another IO

        Returns:
            New IO that sequences this IO with f

        Example:
            >>> def read_file(path: str) -> IO[str]:
            ...     return Effect(lambda: open(path).read())
            >>>
            >>> def write_file(path: str, content: str) -> IO[None]:
            ...     return Effect(lambda: open(path, "w").write(content))
            >>>
            >>> # Chain operations without executing
            >>> copy = read_file("in.txt").flat_map(lambda content: write_file("out.txt", content))
            >>> copy.run()  # Now execute the side effects
        """
        return FlatMapped(self, f)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"{self.__class__.__name__}(...)"


@dataclass(frozen=True)
class Pure(IO[A_co]):
    """Pure value wrapped in IO (no side effects).

    Represents a computation that simply returns a value without
    performing any side effects.

    Example:
        >>> Pure(42).run()
        42
    """

    value: A_co

    def run(self) -> A_co:
        """Return the pure value."""
        return self.value

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"Pure({self.value!r})"


@dataclass(frozen=True)
class Effect(IO[A_co]):
    """Suspended side effect.

    Represents a computation that performs a side effect when executed.
    The side effect is captured in a thunk (zero-argument function) and
    is not executed until .run() is called.

    Example:
        >>> read_file = Effect(lambda: open("data.txt").read())
        >>> # Nothing executed yet!
        >>> content = read_file.run()  # Now file is read
    """

    thunk: Callable[[], A_co]

    def run(self) -> A_co:
        """Execute the side effect and return the result."""
        return self.thunk()

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"Effect({self.thunk})"


@dataclass(frozen=True)
class FlatMapped(IO[B]):
    """Internal type for chaining IO computations.

    Represents the composition of an IO with a function that returns IO.
    This is the mechanism that enables monadic bind (flat_map).

    Users should not construct this directly; use flat_map instead.
    """

    source: IO
    f: Callable[[object], IO[B]]

    def run(self) -> B:
        """Execute the source IO, then apply f and execute the result.

        This implements the sequencing semantics of the IO monad:
        1. Run the source computation to get a value
        2. Apply f to get a new IO computation
        3. Run that computation to get the final result
        """
        a = self.source.run()
        return self.f(a).run()

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"FlatMapped({self.source!r}, {self.f})"


def pure(value: A_co) -> IO[A_co]:  # type: ignore[misc]
    """Create an IO that returns a pure value.

    Args:
        value: The value to wrap

    Returns:
        IO that returns the value when run

    Example:
        >>> pure(42).run()
        42
    """
    return Pure(value)


def effect(thunk: Callable[[], A_co]) -> IO[A_co]:
    """Create an IO from a side-effecting computation.

    Args:
        thunk: Zero-argument function that performs a side effect

    Returns:
        IO that executes the thunk when run

    Example:
        >>> print_hello = effect(lambda: print("Hello"))
        >>> print_hello.run()  # Prints "Hello"
    """
    return Effect(thunk)
