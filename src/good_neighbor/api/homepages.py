"""Homepage API endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from good_neighbor.effects import Failure, Success
from good_neighbor.models import HomepageId
from good_neighbor.services import HomepageService, UserService
from good_neighbor.storage import create_yaml_repositories

logger = logging.getLogger(__name__)

# Initialize repositories and services
# TODO: Use dependency injection in future
repos = create_yaml_repositories()
repos.storage.load()

user_service = UserService(repos.users)
homepage_service = HomepageService(repos.homepages)

router = APIRouter(prefix="/api/homepages", tags=["homepages"])


# Request/Response models
class CreateHomepageRequest(BaseModel):
    """Request model for creating a homepage."""

    name: str
    is_default: bool = False


class UpdateHomepageRequest(BaseModel):
    """Request model for updating a homepage."""

    name: str


class SetDefaultRequest(BaseModel):
    """Request model for setting default homepage."""

    is_default: bool = True


class HomepageResponse(BaseModel):
    """Response model for homepage."""

    homepage_id: str
    user_id: str
    name: str
    is_default: bool
    created_at: str
    updated_at: str


@router.get("/")  # type: ignore[misc]
async def list_homepages() -> list[HomepageResponse]:
    """List all homepages for the default user.

    Returns:
        list[HomepageResponse]: All homepages for the user

    Raises:
        HTTPException: If operation fails
    """
    # Get or create default user
    user_result = user_service.get_or_create_default_user().run()

    if isinstance(user_result, Failure):
        logger.error("Failed to get default user: %s", user_result.error.message)
        raise HTTPException(status_code=500, detail=user_result.error.message)

    if isinstance(user_result, Success):
        user = user_result.value
        # List homepages for user
        homepages_result = homepage_service.list_homepages_for_user(user.user_id).run()

        if isinstance(homepages_result, Failure):
            logger.error("Failed to list homepages: %s", homepages_result.error.message)
            raise HTTPException(status_code=500, detail=homepages_result.error.message)

        if isinstance(homepages_result, Success):
            homepages = homepages_result.value
            logger.info("Listed %d homepages for user %s", len(homepages), user.user_id)
            return [
                HomepageResponse(
                    homepage_id=str(hp.homepage_id),
                    user_id=str(hp.user_id),
                    name=hp.name,
                    is_default=hp.is_default,
                    created_at=hp.created_at.isoformat(),
                    updated_at=hp.updated_at.isoformat(),
                )
                for hp in homepages
            ]

    raise HTTPException(status_code=500, detail="Unexpected error")


@router.post("/")  # type: ignore[misc]
async def create_homepage(request: CreateHomepageRequest) -> HomepageResponse:
    """Create a new homepage for the default user.

    Args:
        request: Homepage creation request

    Returns:
        HomepageResponse: The created homepage

    Raises:
        HTTPException: If creation fails
    """
    # Get or create default user
    user_result = user_service.get_or_create_default_user().run()

    if isinstance(user_result, Failure):
        logger.error("Failed to get default user: %s", user_result.error.message)
        raise HTTPException(status_code=500, detail=user_result.error.message)

    if isinstance(user_result, Success):
        user = user_result.value
        # Create homepage
        create_result = homepage_service.create_homepage(user.user_id, request.name, request.is_default).run()

        if isinstance(create_result, Failure):
            error = create_result.error
            logger.error("Failed to create homepage: %s - %s", error.code, error.message)
            if error.code == "DUPLICATE_ID":
                raise HTTPException(status_code=409, detail=error.message)
            raise HTTPException(status_code=500, detail=error.message)

        if isinstance(create_result, Success):
            homepage = create_result.value
            logger.info("Created homepage: %s - %s", homepage.homepage_id, homepage.name)
            return HomepageResponse(
                homepage_id=str(homepage.homepage_id),
                user_id=str(homepage.user_id),
                name=homepage.name,
                is_default=homepage.is_default,
                created_at=homepage.created_at.isoformat(),
                updated_at=homepage.updated_at.isoformat(),
            )

    raise HTTPException(status_code=500, detail="Unexpected error")


@router.get("/{homepage_id}")  # type: ignore[misc]
async def get_homepage(homepage_id: str) -> HomepageResponse:
    """Get a specific homepage by ID.

    Args:
        homepage_id: Homepage identifier

    Returns:
        HomepageResponse: The requested homepage

    Raises:
        HTTPException: If homepage not found
    """
    result = homepage_service.get_homepage(HomepageId(homepage_id)).run()

    if isinstance(result, Failure):
        logger.error("Failed to get homepage %s: %s", homepage_id, result.error.message)
        raise HTTPException(status_code=500, detail=result.error.message)

    if isinstance(result, Success):
        homepage = result.value
        if homepage is None:
            logger.warning("Homepage not found: %s", homepage_id)
            raise HTTPException(status_code=404, detail="Homepage not found")

        logger.info("Retrieved homepage: %s - %s", homepage.homepage_id, homepage.name)
        return HomepageResponse(
            homepage_id=str(homepage.homepage_id),
            user_id=str(homepage.user_id),
            name=homepage.name,
            is_default=homepage.is_default,
            created_at=homepage.created_at.isoformat(),
            updated_at=homepage.updated_at.isoformat(),
        )

    raise HTTPException(status_code=500, detail="Unexpected error")


@router.put("/{homepage_id}")  # type: ignore[misc]
async def update_homepage(homepage_id: str, request: UpdateHomepageRequest) -> HomepageResponse:
    """Update a homepage's name.

    Args:
        homepage_id: Homepage identifier
        request: Update request

    Returns:
        HomepageResponse: The updated homepage

    Raises:
        HTTPException: If update fails
    """
    update_result = homepage_service.update_homepage_name(HomepageId(homepage_id), request.name).run()

    if isinstance(update_result, Failure):
        error = update_result.error
        logger.error("Failed to update homepage %s: %s - %s", homepage_id, error.code, error.message)
        if error.code == "NOT_FOUND":
            raise HTTPException(status_code=404, detail=error.message)
        raise HTTPException(status_code=500, detail=error.message)

    if isinstance(update_result, Success):
        # Fetch the updated homepage to return
        get_result = homepage_service.get_homepage(HomepageId(homepage_id)).run()

        if isinstance(get_result, Success) and get_result.value is not None:
            homepage = get_result.value
            logger.info("Updated homepage: %s - %s", homepage_id, request.name)
            return HomepageResponse(
                homepage_id=str(homepage.homepage_id),
                user_id=str(homepage.user_id),
                name=homepage.name,
                is_default=homepage.is_default,
                created_at=homepage.created_at.isoformat(),
                updated_at=homepage.updated_at.isoformat(),
            )

    raise HTTPException(status_code=500, detail="Failed to retrieve updated homepage")


@router.patch("/{homepage_id}/default")  # type: ignore[misc]
async def set_default_homepage(homepage_id: str, request: SetDefaultRequest) -> HomepageResponse:
    """Set a homepage as the default.

    Args:
        homepage_id: Homepage identifier
        request: Set default request

    Returns:
        HomepageResponse: The updated homepage

    Raises:
        HTTPException: If operation fails
    """
    # Get default user
    user_result = user_service.get_or_create_default_user().run()

    if isinstance(user_result, Failure):
        logger.error("Failed to get default user: %s", user_result.error.message)
        raise HTTPException(status_code=500, detail=user_result.error.message)

    if isinstance(user_result, Success):
        user = user_result.value
        # Set as default
        set_result = homepage_service.set_default_homepage(HomepageId(homepage_id), user.user_id).run()

        if isinstance(set_result, Failure):
            error = set_result.error
            logger.error("Failed to set default homepage %s: %s - %s", homepage_id, error.code, error.message)
            if error.code == "NOT_FOUND":
                raise HTTPException(status_code=404, detail=error.message)
            if error.code == "FORBIDDEN":
                raise HTTPException(status_code=403, detail=error.message)
            raise HTTPException(status_code=500, detail=error.message)

        if isinstance(set_result, Success):
            # Fetch the updated homepage
            get_result = homepage_service.get_homepage(HomepageId(homepage_id)).run()

            if isinstance(get_result, Success) and get_result.value is not None:
                homepage = get_result.value
                logger.info("Set homepage as default: %s", homepage_id)
                return HomepageResponse(
                    homepage_id=str(homepage.homepage_id),
                    user_id=str(homepage.user_id),
                    name=homepage.name,
                    is_default=homepage.is_default,
                    created_at=homepage.created_at.isoformat(),
                    updated_at=homepage.updated_at.isoformat(),
                )

    raise HTTPException(status_code=500, detail="Failed to retrieve updated homepage")


@router.delete("/{homepage_id}")  # type: ignore[misc]
async def delete_homepage(homepage_id: str) -> dict[str, Any]:
    """Delete a homepage.

    Args:
        homepage_id: Homepage identifier

    Returns:
        dict: Deletion confirmation

    Raises:
        HTTPException: If deletion fails or violates business rules
    """
    # Get default user
    user_result = user_service.get_or_create_default_user().run()

    if isinstance(user_result, Failure):
        logger.error("Failed to get default user: %s", user_result.error.message)
        raise HTTPException(status_code=500, detail=user_result.error.message)

    if isinstance(user_result, Success):
        user = user_result.value
        # Delete homepage
        delete_result = homepage_service.delete_homepage(HomepageId(homepage_id), user.user_id).run()

        if isinstance(delete_result, Failure):
            error = delete_result.error
            logger.error("Failed to delete homepage %s: %s - %s", homepage_id, error.code, error.message)
            if error.code == "NOT_FOUND":
                raise HTTPException(status_code=404, detail=error.message)
            if error.code == "FORBIDDEN":
                raise HTTPException(status_code=403, detail=error.message)
            if error.code == "BUSINESS_RULE_VIOLATION":
                raise HTTPException(status_code=400, detail=error.message)
            raise HTTPException(status_code=500, detail=error.message)

        if isinstance(delete_result, Success):
            logger.info("Deleted homepage: %s", homepage_id)
            return {"status": "deleted", "id": homepage_id}

    raise HTTPException(status_code=500, detail="Unexpected error")
