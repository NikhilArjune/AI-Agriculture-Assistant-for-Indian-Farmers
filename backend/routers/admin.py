from fastapi import APIRouter, Depends, HTTPException

from core.dependencies import require_admin
from models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(
    limit: int = 50,
    offset: int = 0,
    current_admin: User = Depends(require_admin),
):
    users = await User.find_all().skip(offset).limit(limit).to_list()
    return [
        {
            "id": str(u.id),
            "phone": u.phone,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.patch("/users/{user_id}/deactivate", status_code=204)
async def deactivate_user(user_id: str, current_admin: User = Depends(require_admin)):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    await user.set({"is_active": False})


@router.get("/stats")
async def platform_stats(current_admin: User = Depends(require_admin)):
    from models.farmer_profile import FarmerProfile
    from models.chat_history import ChatMessage
    from models.disease_report import DiseaseReport

    total_users = await User.count()
    total_farmers = await FarmerProfile.count()
    total_chats = await ChatMessage.count()
    total_disease_reports = await DiseaseReport.count()

    return {
        "total_users": total_users,
        "total_farmers": total_farmers,
        "total_chat_messages": total_chats,
        "total_disease_reports": total_disease_reports,
    }
