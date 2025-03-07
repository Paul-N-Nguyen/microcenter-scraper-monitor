import httpx
import logging
from scrapers.item import Item
from prefect import task

logger = logging.getLogger()

@task(retries=3, retry_delay_seconds=1)
def send_discord_notification(webhook_url: str, item: Item):
    """
    Sends a notification via Discord webhook
    :param webhook_url: str, discord webhook URL
    :param item: Item
    :return: None
    """
    message = {
        "content": f"In Stock: {item.name} - {item.price}\n{item.link}"
    }

    try:
        with httpx.Client(http2=True) as client:
            response = client.post(webhook_url, json=message, timeout=10)
            response.raise_for_status()
        logger.info(f"Successfully sent notification for {item.name}")
    except httpx.RequestError as e:
        logger.error(f"Failed to send discord notification: {e}")
        raise
