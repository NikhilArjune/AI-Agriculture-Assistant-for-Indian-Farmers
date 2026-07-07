from fastapi import APIRouter, Depends, HTTPException
from beanie import PydanticObjectId

from core.dependencies import require_farmer
from models.notification import Notification
from models.user import User
from schemas.notification import NotificationListResponse, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(require_farmer),
):
    notifications = await Notification.find(
        Notification.farmer_id == current_user.id,
    ).sort("-created_at").skip(offset).limit(limit).to_list()

    unread_count = await Notification.find(
        Notification.farmer_id == current_user.id,
        Notification.is_read == False,
    ).count()

    items = [
        NotificationResponse(
            id=str(n.id),
            type=n.type,
            message=n.message,
            channel=n.channel,
            is_sent=n.is_sent,
            is_read=n.is_read,
            created_at=n.created_at.isoformat(),
        )
        for n in notifications
    ]

    return NotificationListResponse(notifications=items, unread_count=unread_count)


@router.patch("/{notification_id}/read", status_code=204)
async def mark_read(notification_id: str, current_user: User = Depends(require_farmer)):
    notification = await Notification.get(PydanticObjectId(notification_id))
    if not notification or notification.farmer_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found.")

    from datetime import datetime
    await notification.set({"is_read": True, "read_at": datetime.utcnow()})
