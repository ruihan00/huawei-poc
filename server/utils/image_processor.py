from PIL import Image
from utils.model import Model
from utils.tracking import process_frame
import os
from logger import logger
model = Model(".//models/mob-aid.pt")
async def process_image(image: str) -> str:
    processed_image, tracked_objs = await process_frame(image)
    return processed_image
