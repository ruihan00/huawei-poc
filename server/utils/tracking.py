import base64
import time
import io

import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
from PIL import Image, ImageDraw, ImageFont
from .falling import detect_falls, detect_squat
from models import Model


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
    # if image.mode != 'RGB':
    #     image = image.convert('RGB')

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

    # 3. Second model to detect mobility aids
    mob_aids = model_mob_aid(image)

    # 4. Draw all the objects together
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for obj in tracked_objs:
        obj_id = obj.track_id
        x1, y1, x2, y2 = obj.to_ltrb()
        # check for fall
        if detect_falls(x1, x2, y1, y2):
            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
            text_bbox = draw.textbbox((x1, y1), "Fall", font=font)
        # else check for squat/loitering
        elif obj_id in person_last_position:
            last_pos = person_last_position[obj_id]
            if detect_squat(last_pos['y1'], y1):
                draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
                text_bbox = draw.textbbox((x1, y1), "Unnatural Behaviour", font=font)
            else:
                # detect loitering at > 30s
                if person_durations[obj_id] > 30:
                    draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
                    text_bbox = draw.textbbox((x1, y1), "Unnatural Behaviour (Prolonged time in frame)", font=font)
        else:
            draw.rectangle([x1, y1, x2, y2], outline="blue", width=1)


    return image, None
