import asyncio
import base64
import io
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from logger import logger
from concurrent.futures import ThreadPoolExecutor
import uuid
# Initialize model and tracker
tracker = DeepSort(max_age=5)
model = YOLO('yolov8n.pt')

person_durations = {}
person_entry_times = {}

# Create a ThreadPoolExecutor for parallel processing
executor = ThreadPoolExecutor(max_workers=4)

async def process_frame(frame):

    global person_durations, person_entry_times
    # loop = asyncio.get_event_loop()

    # Decode image data and process it in a thread pool
    image_data = base64.b64decode(frame)

    image = Image.open(io.BytesIO(image_data))

    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Run model inference
    t0 = time.time()
    results = model(image)
    t1 = time.time()
    
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
        person = ([x1, y1, x2, y2], conf, name)
        detections.append(person)
    
    # Track objects
    t3 = time.time()
    tracked_objects = tracker.update_tracks(detections, frame=original_image)
    t4 = time.time()
    
    print(f"model={t1-t0:.4f}sec tracking={t4-t3:.4f}sec total={t4-t0:.4f}sec")

    # Draw on image
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

    # Save image and encode to base64
    file_name = f"{uuid.uuid4()}.png"
    file_path = f"./files/{file_name}"
    image.save(file_path, format="PNG")

    return file_name, tracked_objects
