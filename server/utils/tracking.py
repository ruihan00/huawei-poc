import base64
import time
import io

import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
from PIL import Image, ImageDraw, ImageFont
from .falling import detect_falls, detect_squat
from models import Model
from logger import logger

model_yolo = Model("models/yolov8n.pt")

tracker = DeepSort(max_age=5)

model_mob_aid = Model("models/mob-aid.pt")


person_durations = {}
person_entry_times = {}
person_last_position = {}

async def process_frame(base64_img: str):
    # Convert from base64
    image_data = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(image_data))
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # 1. First model to get objects
    results = model_yolo.predict(image)
    
    detections = []

    # 2. Tracker for AI to tell what objects are same between frames
    tracked_objs = tracker.update_tracks(
        [(result.box, result.conf, result.name) for result in results],
        frame=np.array(image),
    )
    current_time = time.time()
    for obj in tracked_objs:
        obj_id = obj.track_id

        if obj_id not in person_entry_times:
            person_entry_times[obj_id] = current_time

        duration = current_time - person_entry_times[obj_id]
        person_durations[obj_id] = duration
        logger.info(person_durations)

    # 3. Second model to detect mobility aids
    # mob_aids = model_mob_aid(image)
    # 4. Draw all the objects together
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for obj in tracked_objs:
        obj_id = obj.track_id
        x1, y1, x2, y2 = obj.to_ltrb()
        last_pos = person_last_position.get(obj_id, None)
        duration = person_durations.get(obj_id, None)
        # check for fall
        fall_ratio = detect_falls(x1, x2, y1, y2)
        if fall_ratio > 1.4:
            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
            draw.text((x1, y1), "Fall", font=font, fill="red")
        # else check for squat/loitering
        elif last_pos and detect_squat(last_pos['y1'], y1):
            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
            draw.text((x1, y1), "Unnatural Behaviour", font=font, fill="red")
            
        elif duration and duration > 30:
            # detect loitering at > 30s
            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
            draw.text((x1, y1), "Unnatural Behaviour (Prolonged time in frame)", font=font, fill="red")
        else:
            draw.rectangle([x1, y1, x2, y2], outline="blue", width=1)
            person_last_position[obj_id] = {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            }
            draw.text((x1, y1), f"{fall_ratio}", font=font, fill="blue")


    return image, None
