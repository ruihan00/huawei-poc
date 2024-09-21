import base64
import time
import uuid
from deep_sort_realtime.deepsort_tracker import DeepSort
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import torch
from utils.model import Model
from logger import logger
from ultralytics import YOLO

if torch.cuda.is_available():
    torch.cuda.set_device(0)
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
logger.info(f'Using device: {device}')

model_yolo = YOLO('yolov8n.pt')
model_yolo.to(device)

tracker = DeepSort(max_age=5)

model_mob_aid = Model("./models/mob-aid.pt")
# TODO: Also set Mob Aid to CUDA
# model_mob_aid.to(device)


person_durations = {}
person_entry_times = {}
async def process_frame(base64_img: str):
    # Convert from base64
    image_data = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(image_data))
    # if image.mode != 'RGB':
    #     image = image.convert('RGB')

    # 1. First model to get objects
    results = model_yolo(image)

    boxes = results[0].boxes.xyxy.tolist()
    classes = results[0].boxes.cls.tolist()
    names = results[0].names
    confidences = results[0].boxes.conf.tolist()
    detections = []

    # Filter unhelpful results
    for box, cls, conf in zip(boxes, classes, confidences):
        if int(cls) != 0 or conf < 0.5:
            continue
        x1, y1, x2, y2 = box
        confidence = conf
        name = names[int(cls)]
        label = f"{name}: {confidence:.2f}"
        person = ([x1, y1, x2, y2], conf, name)
        detections.append(person)

    # 2. Tracker for AI to tell what objects are same between frames
    current_time = time.time()
    tracked_objects = tracker.update_tracks(detections, frame=np.array(image))
    for obj in tracked_objects:
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
    for obj in tracked_objects:
        obj_id = obj.track_id
        x1, y1, x2, y2 = obj.to_ltrb()
        # name = names[int(cls)]
        # label = f"{name}: {confidence:.2f}"
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        # text_bbox = draw.textbbox((x1, y1), label, font=font)
        # text_background = [text_bbox[0], text_bbox[1], text_bbox[2], text_bbox[3]]
        # draw.rectangle(text_background, fill="red")

    return image, None
