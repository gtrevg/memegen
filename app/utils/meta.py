from urllib.parse import unquote

import aiohttp
from sanic.log import logger

from .. import settings


def get_watermark(request, watermark: str) -> tuple[str, bool]:
    updated = False

    if watermark == "none":
        watermark = ""
    elif watermark:
        if watermark == settings.DEFAULT_WATERMARK:
            logger.warning(f"Redundant watermark: {watermark}")
            updated = True
        elif watermark not in settings.ALLOWED_WATERMARKS:
            logger.warning(f"Unknown watermark: {watermark}")
            watermark = settings.DEFAULT_WATERMARK
            updated = True
    else:
        watermark = settings.DEFAULT_WATERMARK

    return watermark, updated


async def track_url(request, lines):
    if settings.REMOTE_TRACKING_URL:  # pragma: no cover
        async with aiohttp.ClientSession() as session:
            params = dict(
                text=" ".join(lines),
                source="memegen.link",
                context=unquote(request.url),
            )
            response = await session.get(settings.REMOTE_TRACKING_URL, params=params)
            if response.status != 200:
                try:
                    message = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    message = response.text
                logger.error(f"Tracker response: {message}")
