import base64
from datetime import datetime
import io

from PIL import Image, ImageDraw, ImageFont

from shapes.sender_message import ReceiverMessage
from utils.tracking import process_frame

DOWNSCALE = None


# Do additional non-AI processing to results from AI code
async def process_image(base64_img: str) -> ReceiverMessage:
    image_data = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(image_data))

    results = await process_frame(image)
    if DOWNSCALE:
        image.thumbnail(
            tuple(DOWNSCALE * x for x in image.size), Image.Resampling.LANCZOS
        )

    # 4. Draw all the objects together
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for result in results:
        x1, y1, x2, y2 = result.box
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

    # Draw debug time
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    now = datetime.now()
    label = f"{now.strftime('%d%m%y %H:%M:%S')}.{now.microsecond // 1e5}"
    draw.text((0, 0), label, font=font, fill="red")

    # Convert image to bytes, then base64
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    b = buffer.getvalue()
    image_data = base64.b64encode(b)

    return ReceiverMessage(image=image_data,
                           objects=results)
