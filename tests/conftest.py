"""Configuration for pytest."""

import contextlib
from collections.abc import Generator
from pathlib import Path

import pytest

from good_neighbor.storage import create_yaml_repositories

# Test storage file location
TEST_STORAGE_PATH = Path("test-storage.yaml")


@pytest.fixture(scope="function", autouse=True)
def test_storage(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Provide isolated test storage that doesn't touch production storage.yaml.

    This fixture:
    - Creates a test-storage.yaml file for each test
    - Cleans up the storage before each test run
    - Preserves test-storage.yaml if tests fail (for debugging)
    - Removes test-storage.yaml if tests pass

    The fixture is autouse=True so it applies to all tests automatically.
    """
    # Clean up any existing test data from previous run
    if TEST_STORAGE_PATH.exists():
        TEST_STORAGE_PATH.unlink()

    # Create test repositories with test storage file
    test_repos = create_yaml_repositories(TEST_STORAGE_PATH)
    test_repos.storage.load()

    # Initialize required test data (user and homepage)
    # This mimics what would exist in production storage
    from datetime import datetime, timezone

    from good_neighbor.models import Homepage, HomepageId, User, UserId

    user_id = UserId("test-user-id")
    homepage_id = HomepageId("test-homepage-id")

    test_user = User(
        user_id=user_id,
        username="testuser",
        default_homepage_id=homepage_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    test_homepage = Homepage(
        homepage_id=homepage_id,
        user_id=user_id,
        name="Test Homepage",
        is_default=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    test_repos.storage.set_user(test_user)
    test_repos.storage.set_homepage(test_homepage)
    test_repos.storage.save()

    # Patch all modules that use repos
    monkeypatch.setattr("good_neighbor.api.widgets.repos", test_repos)
    monkeypatch.setattr("good_neighbor.api.homepages.repos", test_repos)

    # Provide to the test
    yield

    # Clean up test storage file only if test passed
    # If test failed, leave it for debugging
    # If cleanup fails, that's okay - file will be removed next run
    if TEST_STORAGE_PATH.exists():
        with contextlib.suppress(Exception):
            TEST_STORAGE_PATH.unlink()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_storage() -> Generator[None, None, None]:
    """Clean up test storage at the start of test session.

    This ensures a clean slate before running any tests.
    """
    # Clean up at start of session
    if TEST_STORAGE_PATH.exists():
        TEST_STORAGE_PATH.unlink()

    yield

    # Clean up at end of session (after all tests)
    if TEST_STORAGE_PATH.exists():
        TEST_STORAGE_PATH.unlink()
