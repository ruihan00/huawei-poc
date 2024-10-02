import base64
import time
import io

import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
from PIL import Image, ImageDraw, ImageFont

from models import Model
from models.model import ModelResult


model_yolo = Model("models/yolov8n.pt")

tracker = DeepSort(max_age=5)

model_mob_aid = Model("models/mob-aid.pt")


person_durations = {}
person_entry_times = {}


# Put mainly AI code within this function
async def process_frame(image: Image) -> list[ModelResult]:
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
    # results = model_mob_aid(image)


    return results
