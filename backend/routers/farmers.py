from datetime import datetime

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from core.dependencies import get_current_user, require_farmer
from models.farmer_profile import FarmerProfile
from models.user import User
from schemas.farmer import (
    CoordinatesSchema,
    FarmerProfileCreate,
    FarmerProfileResponse,
    FarmerProfileUpdate,
    LocationSchema,
)

router = APIRouter(prefix="/farmers", tags=["farmers"])


@router.post("/profile", response_model=FarmerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(payload: FarmerProfileCreate, current_user: User = Depends(require_farmer)):
    existing = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)
    if existing:
        raise HTTPException(status_code=409, detail="Profile already exists. Use PATCH to update.")

    profile = FarmerProfile(
        user_id=current_user.id,
        **payload.model_dump(),
    )
    await profile.insert()
    return _to_response(profile)


@router.get("/profile", response_model=FarmerProfileResponse)
async def get_profile(current_user: User = Depends(require_farmer)):
    profile = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return _to_response(profile)


@router.patch("/profile", response_model=FarmerProfileResponse)
async def update_profile(payload: FarmerProfileUpdate, current_user: User = Depends(require_farmer)):
    profile = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    update_data = payload.model_dump(exclude_none=True)
    update_data["updated_at"] = datetime.utcnow()

    await profile.set(update_data)
    return _to_response(profile)


def _to_response(profile: FarmerProfile) -> FarmerProfileResponse:
    location = LocationSchema(
        state=profile.location.state,
        district=profile.location.district,
        village=profile.location.village,
        coordinates=CoordinatesSchema(
            lat=profile.location.coordinates.lat,
            lng=profile.location.coordinates.lng,
        ),
    )

    return FarmerProfileResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        full_name=profile.full_name,
        preferred_lang=profile.preferred_lang,
        location=location,
        farm_size_acres=profile.farm_size_acres,
        soil_type=profile.soil_type,
        irrigation_type=profile.irrigation_type,
        primary_crops=profile.primary_crops,
    )
