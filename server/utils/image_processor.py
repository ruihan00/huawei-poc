import base64
from datetime import datetime
import io

from PIL import Image, ImageDraw, ImageFont

from utils.tracking import process_frame

from shapes.sender_message import Event
from utils.external.firestore import EventTable

DOWNSCALE = None

async def process_image(base64_img: str) -> list[Event]:
    image_data = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(image_data))

    events = await process_frame(image)

    for event in events:
        EventTable.create_event(event)

    return events
