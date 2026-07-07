import asyncio
import logging

import httpx
from langchain_core.tools import tool

from core.config import settings

logger = logging.getLogger(__name__)


@tool
def save_notification(farmer_id: str, notification_type: str, message: str, channel: str = "push") -> str:
    """Save a notification to the MongoDB notifications collection.

    Returns the ObjectId string of the saved notification.
    """
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_async_save(farmer_id, notification_type, message, channel))
    except Exception as exc:
        logger.error("NotificationTool: save failed: %s", exc)
        return ""


async def _async_save(farmer_id: str, notification_type: str, message: str, channel: str) -> str:
    from models.notification import Notification
    from beanie import PydanticObjectId

    doc = Notification(
        farmer_id=PydanticObjectId(farmer_id),
        type=notification_type,
        message=message,
        channel=channel,
        is_sent=False,
        is_read=False,
    )
    await doc.insert()
    return str(doc.id)


@tool
def send_notification(farmer_id: str, message: str, channel: str = "push") -> dict:
    """Dispatch a notification via FCM push or SMS.

    Returns dict with: success, channel, message_id.
    """
    if channel == "push":
        return _send_fcm(farmer_id, message)
    elif channel == "sms":
        return _send_sms(farmer_id, message)
    return {"success": False, "error": "Unknown channel"}


def _send_fcm(farmer_id: str, message: str) -> dict:
    if not settings.fcm_server_key:
        logger.warning("NotificationTool: FCM_SERVER_KEY not set, skipping push.")
        return {"success": False, "error": "FCM not configured", "_mock": True}

    try:
        # In production: fetch FCM token from farmer profile
        payload = {
            "to": f"/topics/farmer_{farmer_id}",
            "notification": {"title": "Krishi Sahayak Alert", "body": message},
        }
        resp = httpx.post(
            "https://fcm.googleapis.com/fcm/send",
            json=payload,
            headers={
                "Authorization": f"key={settings.fcm_server_key}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return {"success": True, "channel": "push", "message_id": data.get("message_id")}
    except Exception as exc:
        logger.error("NotificationTool: FCM send failed: %s", exc)
        return {"success": False, "error": str(exc)}


def _send_sms(farmer_id: str, message: str) -> dict:
    if not settings.msg91_auth_key:
        logger.warning("NotificationTool: MSG91_AUTH_KEY not set, skipping SMS.")
        return {"success": False, "error": "SMS not configured", "_mock": True}

    try:
        # Fetch farmer phone from DB (simplified — use profile_tool in production)
        payload = {
            "authkey": settings.msg91_auth_key,
            "mobiles": "91XXXXXXXXXX",
            "message": message,
            "sender": "KRISHS",
            "route": "4",
        }
        resp = httpx.post("https://api.msg91.com/api/sendhttp.php", params=payload, timeout=10)
        resp.raise_for_status()
        return {"success": True, "channel": "sms"}
    except Exception as exc:
        logger.error("NotificationTool: SMS send failed: %s", exc)
        return {"success": False, "error": str(exc)}
