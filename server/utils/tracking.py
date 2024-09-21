import base64
import time
import uuid
from deep_sort_realtime.deepsort_tracker import DeepSort
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import torch
from models import Model
from logger import logger
from ultralytics import YOLO


model_yolo = Model('models/yolov8n.pt')

tracker = DeepSort(max_age=5)

model_mob_aid = Model("models/mob-aid.pt")


person_durations = {}
person_entry_times = {}
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
        frame=np.array(image))
    current_time = time.time()
    for obj in tracked_objs:
        obj_id = obj.track_id

        if obj_id not in person_entry_times:
            person_entry_times[obj_id] = current_time

        duration = current_time - person_entry_times[obj_id]
        person_durations[obj_id] = duration


    # 3. Second model to detect mobility aids
    # results = model_mob_aid(image)


    # 4. Draw all the objects together
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for obj in tracked_objs:
        obj_id = obj.track_id
        x1, y1, x2, y2 = obj.to_ltrb()
        # name = names[int(cls)]
        # label = f"{name}: {confidence:.2f}"
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        # text_bbox = draw.textbbox((x1, y1), label, font=font)
        # text_background = [text_bbox[0], text_bbox[1], text_bbox[2], text_bbox[3]]
        # draw.rectangle(text_background, fill="red")

    return image, None
