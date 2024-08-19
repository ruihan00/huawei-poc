from PIL import Image
from utils.model import Model
import os
model = Model(".//models/mob-aid.pt")
def process_image(image: str) -> str:
    processed_image = model.predict(image)
    return processed_image
