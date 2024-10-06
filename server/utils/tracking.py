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
tracker = DeepSort(max_iou_distance=0.5, max_age=30, n_init=3)
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
    frames = [(frame['frame'].copy(), frame['tracked_objs']) for frame in video_entries]
    for frame, tracked_objs in frames:
        for obj in tracked_objs:
            if obj.id == person_id:
                x1, y1, x2, y2 = obj.box
                draw = ImageDraw.Draw(frame)
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                font = ImageFont.load_default()
                draw.text((x1, y1), f"Person {person_id}", font=font, fill="red")
            else:
                frames.remove((frame, tracked_objs))
    # save video to mp4
    video_name = f"videos/{person_id}-{time.time()}.webm"
    
    video_writer = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'vp80'), 5, (video_entries[0]['frame'].width, video_entries[0]['frame'].height))
    for frame in frames:
        video_writer.write(cv2.cvtColor(np.array(frame[0]), cv2.COLOR_RGB2BGR))
    
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

    
    # filter low confidence and non-person detections
    
    # save a copy of the image with bounding boxes
    clone_image = image.copy()
    draw = ImageDraw.Draw(clone_image)
    

    # 2. Tracker for AI to tell what objects are same between frames
    # tracked_objs = tracker.update_tracks(
    frame_id = add_to_history(image, results)['id']
    current_time = time.time()
    for obj in results:
        obj_id = obj.id
        x1, y1, x2, y2 = obj.box
        if obj_id not in person_entry_times:
            person_entry_times[obj_id] = current_time

        duration = current_time - person_entry_times[obj_id]
        if obj_id in ignore_persons.keys():
            continue
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        font = ImageFont.load_default()
        draw.text((x1, y1), f"Person {obj_id}", font=font, fill="red")
        clone_image.save(f"images/{current_time}.jpg")
        # detect fall
        if is_falling(x1, x2, y1, y2):
            print(f"Person {obj_id} is falling, position: {x1, y1, x2, y2}")
            video = await create_video(frame_id - 50, frame_id, obj_id)

            events.append(Event(type="Fall", url=video, timestamp=get_time_now()))
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
