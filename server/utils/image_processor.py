import base64
from datetime import datetime
import io

from PIL import Image, ImageDraw, ImageFont

from shapes.sender_message import ReceiverMessage
from utils.tracking import process_frame

DOWNSCALE = None


async def process_image(base64_img: str) -> ReceiverMessage:
    # client_packet = {
    #     "camera_id": websocket_host,
    #     "image": base64_img
    # }

    img_processed, tracked_objs = await process_frame(base64_img)
    if DOWNSCALE:
        img_processed.thumbnail(
            tuple(DOWNSCALE * x for x in img_processed.size), Image.Resampling.LANCZOS
        )

    # Draw boxes on image
    draw = ImageDraw.Draw(img_processed)
    font = ImageFont.load_default()
    now = datetime.now()
    label = f"{now.strftime('%d%m%y %H:%M:%S')}.{now.microsecond // 1e5}"
    draw.text((0, 0), label, font=font, fill="red")

    # Convert image to bytes, then base64
    buffer = io.BytesIO()
    img_processed.save(buffer, format="PNG")
    b = buffer.getvalue()
    image_data = base64.b64encode(b)

    return ReceiverMessage(image=image_data)
