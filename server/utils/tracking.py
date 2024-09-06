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

# Initialize model and tracker
tracker = DeepSort()

person_durations = {}
person_entry_times = {}

# Create a ThreadPoolExecutor for parallel processing
executor = ThreadPoolExecutor(max_workers=4)

async def process_frame(frame):
    model = YOLO('yolov8n.pt')

    global person_durations, person_entry_times
    loop = asyncio.get_event_loop()
    
    # Decode image data and process it in a thread pool
    image_data = base64.b64decode(frame)
    
    # Load and process image asynchronously
    image = await loop.run_in_executor(executor, lambda: Image.open(io.BytesIO(image_data)))
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Run model inference
    results = await loop.run_in_executor(executor, lambda: model(image))
    
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
    tracked_objects = await loop.run_in_executor(executor, lambda: tracker.update_tracks(detections, frame=original_image))

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
    buffered = io.BytesIO()
    await loop.run_in_executor(executor, lambda: image.save(buffered, format="PNG"))
    base64_image = await loop.run_in_executor(executor, lambda: base64.b64encode(buffered.getvalue()).decode('utf-8'))
    
    return base64_image, tracked_objects
