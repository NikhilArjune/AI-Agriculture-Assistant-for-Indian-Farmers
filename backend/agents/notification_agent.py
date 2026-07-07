import logging

from agents.state import AgriState
from tools.profile_tool import fetch_farmer_profile
from tools.notification_tool import send_notification, save_notification

logger = logging.getLogger(__name__)


def run_notification_agent(state: AgriState) -> AgriState:
    user_id = state["user_id"]
    query = state.get("query", "")
    tool_outputs = state.get("tool_outputs", {})

    profile = fetch_farmer_profile(user_id)
    language = profile.get("preferred_lang", "en")

    # Determine notification type from context
    alert_type = "general"
    if any(kw in query.lower() for kw in ("weather", "rain", "frost", "heat")):
        alert_type = "weather_alert"
    elif any(kw in query.lower() for kw in ("price", "mandi", "rate")):
        alert_type = "price_alert"
    elif any(kw in query.lower() for kw in ("scheme", "deadline", "last date")):
        alert_type = "scheme_deadline"

    message = tool_outputs.get("notification_message", query)

    # Save to MongoDB notifications collection
    notification_id = save_notification.invoke(
        {
            "farmer_id": user_id,
            "notification_type": alert_type,
            "message": message,
            "channel": "push",
        }
    )

    # Dispatch via FCM / SMS
    send_result = send_notification.invoke(
        {
            "farmer_id": user_id,
            "message": message,
            "channel": "push",
        }
    )

    response = f"Notification sent: {message}"
    logger.info(
        "NotificationAgent: user=%s type=%s sent=%s",
        user_id, alert_type, send_result.get("success"),
    )

    return {
        **state,
        "farmer_profile": profile,
        "agent_response": response,
        "confidence": 1.0,
        "tool_outputs": {**tool_outputs, "notification": send_result, "notification_id": notification_id},
    }
