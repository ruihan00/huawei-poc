from PIL import Image
from utils.model import Model
from utils.tracking import process_frame
import os
from logger import logger
model = Model(".//models/mob-aid.pt")
def process_image(image: str) -> str:
    processed_image, tracked_objs = process_frame(image)
    logger.info(tracked_objs)
    return processed_image
