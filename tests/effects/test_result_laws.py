"""Property-based tests for Result monad laws.

These tests verify that the Result monad satisfies the functor and monad laws
using property-based testing with Hypothesis.
"""

from hypothesis import given
from hypothesis import strategies as st

from good_neighbor.effects import Failure, Result, Success


def add_one(x: int) -> int:
    """Test function: add 1."""
    return x + 1


def multiply_two(x: int) -> int:
    """Test function: multiply by 2."""
    return x * 2


def lift_add_one(x: int) -> Result[str, int]:
    """Lift add_one into Result."""
    return Success(x + 1)


def lift_multiply_two(x: int) -> Result[str, int]:
    """Lift multiply_two into Result."""
    return Success(x * 2)


def divide_by(divisor: int) -> Result[str, float]:
    """Division that may fail."""
    if divisor == 0:
        return Failure("Division by zero")
    return Success(1.0 / divisor)


class TestResultFunctorLaws:
    """Test functor laws for Result monad."""

    @given(st.integers())
    def test_functor_identity_success(self, x: int) -> None:
        """Functor law: result.map(lambda a: a) == result (Success case)."""
        result: Result[str, int] = Success(x)

        # map with identity should be the same as original
        assert result.map(lambda a: a) == result

    @given(st.text())
    def test_functor_identity_failure(self, error: str) -> None:
        """Functor law: result.map(lambda a: a) == result (Failure case)."""
        result: Result[str, int] = Failure(error)

        # map with identity should be the same as original
        mapped = result.map(lambda a: a)
        assert isinstance(mapped, Failure)
        assert mapped.error == error

    @given(st.integers())
    def test_functor_composition_success(self, x: int) -> None:
        """Functor law: result.map(f).map(g) == result.map(lambda a: g(f(a))) (Success)."""
        result: Result[str, int] = Success(x)

        # Map f then g
        result1 = result.map(add_one).map(multiply_two)

        # Map composition
        result2 = result.map(lambda a: multiply_two(add_one(a)))

        assert result1 == result2

    @given(st.text())
    def test_functor_composition_failure(self, error: str) -> None:
        """Functor law: Failure propagates unchanged through map."""
        result: Result[str, int] = Failure(error)

        result1 = result.map(add_one).map(multiply_two)
        result2 = result.map(lambda a: multiply_two(add_one(a)))

        assert isinstance(result1, Failure)
        assert isinstance(result2, Failure)
        assert result1.error == error
        assert result2.error == error


class TestResultMonadLaws:
    """Test monad laws for Result."""

    @given(st.integers())
    def test_left_identity(self, x: int) -> None:
        """Monad law: Success(x).flat_map(f) == f(x)."""
        # Success(x).flat_map(f)
        result1 = Success(x).flat_map(lift_add_one)

        # f(x)
        result2 = lift_add_one(x)

        assert result1 == result2

    @given(st.integers())
    def test_right_identity_success(self, x: int) -> None:
        """Monad law: result.flat_map(Success) == result (Success case)."""
        result: Result[str, int] = Success(x)

        # result.flat_map(Success)
        result1 = result.flat_map(lambda a: Success(a))

        # result
        result2 = result

        assert result1 == result2

    @given(st.text())
    def test_right_identity_failure(self, error: str) -> None:
        """Monad law: result.flat_map(Success) == result (Failure case)."""
        result: Result[str, int] = Failure(error)

        result1 = result.flat_map(lambda a: Success(a))

        assert isinstance(result1, Failure)
        assert result1.error == error

    @given(st.integers())
    def test_associativity_success(self, x: int) -> None:
        """Monad law: result.flat_map(f).flat_map(g) == result.flat_map(lambda a: f(a).flat_map(g))."""
        result: Result[str, int] = Success(x)

        # result.flat_map(f).flat_map(g)
        result1 = result.flat_map(lift_add_one).flat_map(lift_multiply_two)

        # result.flat_map(lambda a: f(a).flat_map(g))
        result2 = result.flat_map(lambda a: lift_add_one(a).flat_map(lift_multiply_two))

        assert result1 == result2

    @given(st.text())
    def test_associativity_failure(self, error: str) -> None:
        """Monad law: Failure short-circuits associativity."""
        result: Result[str, int] = Failure(error)

        result1 = result.flat_map(lift_add_one).flat_map(lift_multiply_two)
        result2 = result.flat_map(lambda a: lift_add_one(a).flat_map(lift_multiply_two))

        assert isinstance(result1, Failure)
        assert isinstance(result2, Failure)
        assert result1.error == error
        assert result2.error == error


class TestResultComposition:
    """Test Result composition patterns."""

    @given(st.integers())
    def test_map_flat_map_composition(self, x: int) -> None:
        """Test that map and flat_map can be composed."""
        result: Result[str, int] = Success(x)

        # Using map then flat_map
        result1 = result.map(add_one).flat_map(lift_multiply_two)

        # Using flat_map then map
        result2 = result.flat_map(lift_add_one).map(multiply_two)

        assert result1 == result2

    @given(st.integers(min_value=1, max_value=100))
    def test_error_propagation(self, x: int) -> None:
        """Test that errors propagate through chains."""
        # Chain that fails in the middle
        result = Success(x).flat_map(lambda _: divide_by(0)).flat_map(lambda _: Success(42))

        assert isinstance(result, Failure)
        assert result.error == "Division by zero"

    @given(st.integers(min_value=1, max_value=100))
    def test_short_circuit_on_failure(self, x: int) -> None:
        """Test that Failure short-circuits further operations."""
        call_count = [0]

        def increment_counter(y: int) -> Result[str, int]:
            call_count[0] += 1
            return Success(y)

        # Start with failure
        result = Failure("error").flat_map(increment_counter).flat_map(increment_counter)

        # Function should not be called
        assert call_count[0] == 0
        assert isinstance(result, Failure)
        assert result.error == "error"


class TestResultHelpers:
    """Test Result helper methods."""

    @given(st.integers())
    def test_is_success(self, x: int) -> None:
        """Test is_success() method."""
        success = Success(x)
        failure = Failure("error")

        assert success.is_success()
        assert not failure.is_success()

    @given(st.integers())
    def test_is_failure(self, x: int) -> None:
        """Test is_failure() method."""
        success = Success(x)
        failure = Failure("error")

        assert not success.is_failure()
        assert failure.is_failure()

    @given(st.text())
    def test_map_error(self, error: str) -> None:
        """Test map_error() to transform errors."""
        failure: Result[str, int] = Failure(error)

        transformed = failure.map_error(lambda e: e.upper())

        assert isinstance(transformed, Failure)
        assert transformed.error == error.upper()

    @given(st.integers())
    def test_map_error_noop_on_success(self, x: int) -> None:
        """Test map_error() is no-op on Success."""
        success: Result[str, int] = Success(x)

        result = success.map_error(lambda e: e.upper())

        assert result == success
