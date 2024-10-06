import base64
import time
import io

import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
from PIL import Image, ImageDraw, ImageFont
from .push import async_upload_blob
from models import Model
from models.model import ModelResult
from shapes.sender_message import Event
from .falling import is_falling
from datetime import datetime
from logger import logger
import cv2
model_yolo = Model("models/yolov8n.pt")
tracker = DeepSort(max_age=5)
ignore_persons = {}
model_mob_aid = Model("models/mob-aid.pt")
history = []

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
def remove_expired_history(expiry_time):
    current_time = time.time()
    for history_item in history:
        if current_time - history_item["timestamp"] > expiry_time:
            history.remove(history_item)
def add_to_history(frame:Image, tracked_objs: list):
    history_entry = {
        "id": len(history),
        "frame": frame,
        "tracked_objs": tracked_objs,
        "timestamp": time.time()
    }
    history.append(history_entry)
    return history_entry
    
# create a video from 
async def create_video(start: int, end: int, person_id:int):
    if start < 0:
        start = 0
    video_entries = history[start:end]
    # highlight person_id in each frame
    frames = []
    for entry in video_entries:
        frame = entry["frame"]

        frame = frame.copy()
        
        tracked_objs = entry["tracked_objs"]
        for obj in tracked_objs:
            if obj.track_id == person_id:
                x1, y1, x2, y2 = obj.to_ltrb()
                draw = ImageDraw.Draw(frame)
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                font = ImageFont.load_default()
                draw.text((x1, y1), f"Person {person_id}", font=font, fill="red")
                frames.append(frame)
    # save video to mp4
    video_name = f"videos/{person_id}-{time.time()}.webm"
    
    video_writer = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'vp80'), 5, (frames[0].width, frames[0].height))
    for frame in frames:
        video_writer.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
    
    video_writer.release()
    # convert video to bytes
    with open(video_name, "rb") as video_file:
        video_bytes = video_file.read()
    # upload video to cloud
    video_url = await async_upload_blob(video_bytes, "video/webm")
    return video_url
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
    frame_id = add_to_history(image, tracked_objs)['id']
    current_time = time.time()
    for obj in tracked_objs:
        obj_id = obj.track_id
        x1, y1, x2, y2 = obj.to_ltrb()
        if obj_id not in person_entry_times:
            person_entry_times[obj_id] = current_time

        duration = current_time - person_entry_times[obj_id]
        if obj_id in ignore_persons.keys():
            continue

        # detect fall
        if is_falling(x1, x2, y1, y2):
            print(f"Person {obj_id} is falling, position: {x1, y1, x2, y2}")
            video = await create_video(frame_id - 50, frame_id, obj_id)

            events.append(Event(type="fall", url=video, timestamp=get_time_now()))
            ignore_person_for(obj_id, 10)
        # detect prolonged time in frame
        if duration > 10:
            video = await create_video(frame_id - 50, frame_id, obj_id)
            events.append(Event(type="Prolonged Time", url=video, timestamp=get_time_now()))
            ignore_person_for(obj_id, 20)
        
        person_durations[obj_id] = duration
    # remove historical data older than 60 seconds
    remove_expired_history(180)
    check_people_ignored()

    return events
