from ultralytics import YOLO
import cv2
import numpy as np
import time
from deep_sort_realtime.deepsort_tracker import DeepSort
import base64
import io
from PIL import Image, ImageDraw, ImageFont
from logger import logger
model = YOLO('yolov8n.pt') 

tracker = DeepSort()

person_durations = {}

person_entry_times = {}

def process_frame(frame):
    global person_durations, person_entry_times
    image_data = base64.b64decode(frame)
    image = Image.open(io.BytesIO(image_data))
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    results = model(image)
    boxes = results[0].boxes.xyxy.tolist()
    classes = results[0].boxes.cls.tolist()
    names = results[0].names
    confidences = results[0].boxes.conf.tolist()
    original_image = np.array(image)
    detections = []
    for box, cls, conf in zip(boxes, classes, confidences):
            if int(cls) != 0 or conf < 0.5:
                continue
            x1, y1, x2, y2 = box
            confidence = conf
            name = names[int(cls)]
            label = f"{name}: {confidence:.2f}"
            person =([x1, y1, x2, y2], conf, name )
            detections.append(person)
    tracked_objects = tracker.update_tracks(detections, frame=original_image)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    current_time = time.time()
    for obj in tracked_objects:
        obj_id = obj.track_id
        x1, y1, x2, y2 = obj.to_ltrb()
        logger.info(f"Object ID: {obj_id}, Bounding Box: ({x1}, {y1}, {x2}, {y2})")
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        draw.text((x1, y1), f"ID: {obj_id}", fill="white", font=font)
        if obj_id not in person_entry_times:
            person_entry_times[obj_id] = current_time  

        duration = current_time - person_entry_times[obj_id] 
        person_durations[obj_id] = duration

    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return base64_image, tracked_objects

