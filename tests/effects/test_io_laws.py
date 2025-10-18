"""Property-based tests for IO monad laws.

These tests verify that the IO monad satisfies the functor and monad laws
using property-based testing with Hypothesis.
"""

from hypothesis import given
from hypothesis import strategies as st

from good_neighbor.effects import IO, Effect, Pure


def add_one(x: int) -> int:
    """Test function: add 1."""
    return x + 1


def multiply_two(x: int) -> int:
    """Test function: multiply by 2."""
    return x * 2


def lift_add_one(x: int) -> IO[int]:
    """Lift add_one into IO."""
    return Pure(x + 1)


def lift_multiply_two(x: int) -> IO[int]:
    """Lift multiply_two into IO."""
    return Pure(x * 2)


class TestIOFunctorLaws:
    """Test functor laws for IO monad."""

    @given(st.integers())
    def test_functor_identity(self, x: int) -> None:
        """Functor law: io.map(lambda a: a) == io.

        The identity function should not change the IO.
        """
        io: IO[int] = Pure(x)

        # map with identity should be the same as original
        assert io.map(lambda a: a).run() == io.run()

    @given(st.integers())
    def test_functor_composition(self, x: int) -> None:
        """Functor law: io.map(f).map(g) == io.map(lambda a: g(f(a))).

        Mapping f then g should be the same as mapping the composition.
        """
        io: IO[int] = Pure(x)

        # Map f then g
        result1 = io.map(add_one).map(multiply_two).run()

        # Map composition
        result2 = io.map(lambda a: multiply_two(add_one(a))).run()

        assert result1 == result2

    @given(st.integers())
    def test_functor_composition_with_effect(self, x: int) -> None:
        """Functor composition law also holds for Effect."""
        io: IO[int] = Effect(lambda: x)

        result1 = io.map(add_one).map(multiply_two).run()
        result2 = io.map(lambda a: multiply_two(add_one(a))).run()

        assert result1 == result2


class TestIOMonadLaws:
    """Test monad laws for IO."""

    @given(st.integers())
    def test_left_identity(self, x: int) -> None:
        """Monad law: Pure(x).flat_map(f) == f(x).

        Wrapping a value and immediately flat_mapping should be the same
        as just calling the function.
        """
        # Pure(x).flat_map(f)
        result1 = Pure(x).flat_map(lift_add_one).run()

        # f(x)
        result2 = lift_add_one(x).run()

        assert result1 == result2

    @given(st.integers())
    def test_right_identity(self, x: int) -> None:
        """Monad law: io.flat_map(Pure) == io.

        flat_mapping with Pure should not change the IO.
        """
        io: IO[int] = Pure(x)

        # io.flat_map(Pure)
        result1 = io.flat_map(lambda a: Pure(a)).run()

        # io
        result2 = io.run()

        assert result1 == result2

    @given(st.integers())
    def test_right_identity_with_effect(self, x: int) -> None:
        """Right identity also holds for Effect."""
        io: IO[int] = Effect(lambda: x)

        result1 = io.flat_map(lambda a: Pure(a)).run()
        result2 = io.run()

        assert result1 == result2

    @given(st.integers())
    def test_associativity(self, x: int) -> None:
        """Monad law: io.flat_map(f).flat_map(g) == io.flat_map(lambda a: f(a).flat_map(g)).

        The order of flat_mapping should not matter.
        """
        io: IO[int] = Pure(x)

        # io.flat_map(f).flat_map(g)
        result1 = io.flat_map(lift_add_one).flat_map(lift_multiply_two).run()

        # io.flat_map(lambda a: f(a).flat_map(g))
        result2 = io.flat_map(lambda a: lift_add_one(a).flat_map(lift_multiply_two)).run()

        assert result1 == result2

    @given(st.integers())
    def test_associativity_with_effect(self, x: int) -> None:
        """Associativity also holds for Effect."""
        io: IO[int] = Effect(lambda: x)

        result1 = io.flat_map(lift_add_one).flat_map(lift_multiply_two).run()
        result2 = io.flat_map(lambda a: lift_add_one(a).flat_map(lift_multiply_two)).run()

        assert result1 == result2


class TestIOComposition:
    """Test IO composition patterns."""

    @given(st.integers())
    def test_map_flat_map_composition(self, x: int) -> None:
        """Test that map and flat_map can be composed."""
        io: IO[int] = Pure(x)

        # Using map then flat_map
        result1 = io.map(add_one).flat_map(lift_multiply_two).run()

        # Using flat_map then map
        result2 = io.flat_map(lift_add_one).map(multiply_two).run()

        assert result1 == result2

    @given(st.integers(), st.integers())
    def test_multiple_effects_chain(self, x: int, y: int) -> None:
        """Test chaining multiple effects."""
        counter = [0]  # Mutable counter to verify effects run

        def increment_counter() -> int:
            counter[0] += 1
            return counter[0]

        io: IO[int] = Effect(increment_counter).flat_map(lambda _: Effect(increment_counter))

        result = io.run()

        # Should have incremented twice
        assert counter[0] == 2
        assert result == 2
