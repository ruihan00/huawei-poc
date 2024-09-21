import io
from PIL import Image
from utils.model import Model
from utils.tracking import process_frame
import os
from logger import logger

async def process_image(base64_img: str) -> bytes:
    # client_packet = {
    #     "camera_id": websocket_host,
    #     "image": base64_img
    # }

    img_processed, tracked_objs = await process_frame(base64_img)

    buffer = io.BytesIO()
    img_processed.save(buffer, format="PNG")
    return buffer.getvalue()
