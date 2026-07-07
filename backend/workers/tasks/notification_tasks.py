import logging
from datetime import datetime

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_bulk_weather_alerts(self, district: str, state: str, message: str, channel: str = "push"):
    """Send weather alerts to all farmers in a district."""
    try:
        import asyncio
        from pymongo import AsyncMongoClient
        from core.config import settings

        async def _run():
            client = AsyncMongoClient(settings.mongo_uri)
            db = client[settings.mongo_db_name]
            farmers = await db["farmer_profiles"].find(
                {"location.district": district, "location.state": state},
                {"user_id": 1},
            ).to_list(length=1000)

            from tools.notification_tool import send_notification
            sent = 0
            for f in farmers:
                result = send_notification.invoke({
                    "farmer_id": str(f["user_id"]),
                    "message": message,
                    "channel": channel,
                })
                if result.get("success"):
                    sent += 1

            await client.close()
            return sent

        loop = asyncio.new_event_loop()
        count = loop.run_until_complete(_run())
        loop.close()
        logger.info("Sent weather alerts to %d farmers in %s, %s", count, district, state)
        return {"status": "ok", "sent_count": count}

    except Exception as exc:
        logger.error("send_bulk_weather_alerts failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2)
def send_market_price_digest(self, farmer_id: str, commodities: list[str]):
    """Send daily market price digest to a farmer."""
    try:
        from tools.market_tool import get_mandi_prices
        from tools.notification_tool import send_notification

        summaries = []
        for commodity in commodities[:3]:
            prices = get_mandi_prices.invoke({
                "commodity": commodity,
                "district": "",
                "state": "",
            })
            if prices:
                summaries.append(f"{commodity}: ₹{prices[0].get('modal_price', 'N/A')}/q")

        if summaries:
            message = "Today's prices — " + ", ".join(summaries)
            send_notification.invoke({
                "farmer_id": farmer_id,
                "message": message,
                "channel": "push",
            })

        return {"status": "ok"}
    except Exception as exc:
        logger.error("send_market_price_digest failed: %s", exc)
        raise self.retry(exc=exc)
