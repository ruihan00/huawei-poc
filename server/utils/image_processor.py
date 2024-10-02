from datetime import datetime
import io

from PIL import Image, ImageDraw, ImageFont

from utils.tracking import process_frame

DOWNSCALE = None


async def process_image(base64_img: str) -> bytes:
    # client_packet = {
    #     "camera_id": websocket_host,
    #     "image": base64_img
    # }

    img_processed, tracked_objs = await process_frame(base64_img)
    if DOWNSCALE:
        img_processed.thumbnail(
            tuple(DOWNSCALE * x for x in img_processed.size), Image.Resampling.LANCZOS
        )

    draw = ImageDraw.Draw(img_processed)
    font = ImageFont.load_default()
    now = datetime.now()
    label = f"{now.strftime('%d%m%y %H:%M:%S')}.{now.microsecond // 1e5}"
    draw.text((0, 0), label, font=font, fill="red")

    buffer = io.BytesIO()
    img_processed.save(buffer, format="PNG")
    return buffer.getvalue()