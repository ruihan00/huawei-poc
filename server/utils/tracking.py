import base64
import time
import io

import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
from PIL import Image, ImageDraw, ImageFont

from models import Model
from models.model import ModelResult
from shapes.sender_message import Event
from .falling import is_falling
from datetime import datetime
from logger import logger
model_yolo = Model("models/yolov8m.pt")
tracker = DeepSort(max_age=5)
ignore_persons = {}
model_mob_aid = Model("models/mob-aid.pt")


person_durations = {}
person_entry_times = {}
# get time in dd:mm:yyyy hh:mm:ss
def get_time_now():
    return datetime.now().strftime("%d:%m:%Y %H:%M:%S")

def ignore_person_for(person_id, duration):
    ignore_deadline = time.time() + duration
    ignore_persons[person_id] = ignore_deadline

def check_people_ignored():
    current_time = time.time()
    try:
        for person_id, deadline in ignore_persons.items():
            if current_time > deadline:
                ignore_persons.pop(person_id)
    except RuntimeError:
        pass
# Put mainly AI code within this function
async def process_frame(image: Image) -> list[ModelResult]:
    # 1. First model to get objects
    results = model_yolo.predict(image)
    events = []
    detections = []
    boxes = results[0].boxes.xyxy.tolist()
    classes = results[0].boxes.cls.tolist()
    names = results[0].names
    confidences = results[0].boxes.conf.tolist()
    original_image = np.array(image)
    detections = []
    
    # filter low confidence and non-person detections
    for box, cls, conf in zip(boxes, classes, confidences):
        if int(cls) != 0 or conf < 0.5:
            continue
        x1, y1, x2, y2 = box
        name = names[int(cls)]
        person = ([x1, y1, x2, y2], conf, name)
        detections.append(person)
        
    # 2. Tracker for AI to tell what objects are same between frames
    tracked_objs = tracker.update_tracks(
        detections,
        frame=original_image,
    )
    current_time = time.time()
    for obj in tracked_objs:
        obj_id = obj.track_id
        x1, y1, x2, y2 = obj.to_ltrb()
        if obj_id not in person_entry_times:
            person_entry_times[obj_id] = current_time

        duration = current_time - person_entry_times[obj_id]
        if obj_id in ignore_persons.keys():
            continue
        print(f"Person {obj_id} has been in frame for {duration} seconds")
        print(f"Person {obj_id} is at {x1, y1, x2, y2}")
        # Temporary code to see fall ratio
        fall_ratio = (x2 - x1) / (y2 - y1)
        # draw on image and save as ccurrent time
        draw = ImageDraw.Draw(image)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        font = ImageFont.load_default()
        draw.text((x1, y1), f"Person {obj_id}, ratio {fall_ratio}", font=font, fill="red")
        image.save(f"images/{current_time}.jpg")

        # detect fall
        if is_falling(x1, x2, y1, y2):
            print(f"Person {obj_id} is falling, position: {x1, y1, x2, y2}")
            events.append(Event(type="fall", url="WORK IN PROGRESS", timestamp=get_time_now()))
            ignore_person_for(obj_id, 10)
        # detect prolonged time in frame
        if duration > 10:
            events.append(Event(type="Prolonged Time", url="WORK IN PROGRESS", timestamp=get_time_now()))
            ignore_person_for(obj_id, 20)
        
        check_people_ignored()
        person_durations[obj_id] = duration


    return events
