import base64
from datetime import datetime
import io

from PIL import Image, ImageDraw, ImageFont

from shapes.sender_message import ReceiverMessage
from utils.tracking import process_frame

DOWNSCALE = None


async def process_image(base64_img: str) -> ReceiverMessage:
    image_data = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(image_data))

    events = await process_frame(image)


    return events
