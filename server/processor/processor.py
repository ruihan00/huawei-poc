import base64
import io
import time
import traceback
import uuid

from deep_sort_realtime.deepsort_tracker import DeepSort
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel
from shapes.events import Event, FallEvent, ProlongedTimeEvent, EventCache
import cv2
import numpy as np

from models import Model
from models.model import ModelObject
from shapes.events import Event, FallEvent, ProlongedTimeEvent
from utils.external.firestore import EventTable
from utils.external.push import async_upload_blob
from utils.falling import is_falling
from utils.logger import logger
from utils.time import get_formatted_now


class ProcessorResult(BaseModel):
    # All events to be broadcasted to all receivers
    events: list[Event]
    # Objects for debugging
    objects: list[ModelObject]

class Processor:
    def __init__(self):
        self.model_yolo = Model("models/yolov8n.pt", classes=[0])
        self.tracker = DeepSort(max_iou_distance=0.5, max_age=30, n_init=3)
        self.ignore_persons = {}
        self.model_mob_aid = Model("models/mob-aid.pt")
        self.history = []
        self.event_cache = []
        self.person_durations = {}
        self.person_entry_times = {}

    def ignore_person_for(self, person_id, duration):
        ignore_deadline = time.time() + duration
        self.ignore_persons[person_id] = ignore_deadline

    def check_people_ignored(self):
        current_time = time.time()
        try:
            for person_id, deadline in self.ignore_persons.items():
                if current_time > deadline:
                    try:
                        self.ignore_persons.pop(person_id)
                    except:
                        logger.debug('Error removing ignored person')
                        traceback.print_exc()

        except RuntimeError:
            logger.debug('Runtime error in check_people_ignored')
            traceback.print_exc()

    async def process_events(self, latest_frame, latest_tracked_objs):
        for event in self.event_cache:
            event_person_id = event.person_id
            event_id = event.event_id
            frame = latest_frame.copy()
            for obj in latest_tracked_objs:
                if obj.id == event_person_id:
                    x1, y1, x2, y2 = obj.box
                    draw = ImageDraw.Draw(frame)
                    draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                    font = ImageFont.load_default()
                    draw.text((x1, y1), f"Person {event_person_id}", font=font, fill="red")
            event.video_frames.append((frame.copy(), latest_tracked_objs))
            event.frames_left -= 1
            if event.frames_left <= 0:
                video_name = f"videos/{event_person_id}-{time.time()}.webm"

                video_writer = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'vp80'), 5, (640, 480))
                for frame in event.video_frames:
                    video_writer.write(cv2.cvtColor(np.array(frame[0]), cv2.COLOR_RGB2BGR))

                video_writer.release()
                # convert video to bytes
                with open(video_name, "rb") as video_file:
                    video_bytes = video_file.read()
                # upload video to cloud
                video_url = await async_upload_blob(video_bytes, "video/webm", filename=event_id)



    def remove_expired_history(self, expiry_time):
        current_time = time.time()
        for history_item in self.history:
            if current_time - history_item["timestamp"] > expiry_time:
                try:
                    self.history.remove(history_item)
                except:
                    logger.debug("Error removing history")
                    traceback.print_exc()

    def add_to_history(self, frame: Image, tracked_objs: list):
        history_entry = {
            "id": len(self.history),
            "frame": frame,
            "tracked_objs": tracked_objs,
            "timestamp": time.time()
        }
        self.history.append(history_entry)
        return history_entry

    # create a video from
    async def create_video(self, start: int, end: int, person_id:int, event_id: str):
        if start < 0:
            start = 0
        video_entries = self.history[start:end]
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
        video_url = await async_upload_blob(video_bytes, "video/webm", event_id)
        return video_url, frames


    # Put mainly AI code within this function
    async def process_frame(self, image: Image) -> ProcessorResult:
        # 1. First model to get objects
        objects = self.model_yolo.predict(image)
        events: list[Event] = []

        frame_id = self.add_to_history(image, objects)['id']
        current_time = time.time()
        for obj in objects:
            obj_id = obj.id
            x1, y1, x2, y2 = obj.box
            if obj_id not in self.person_entry_times:
                self.person_entry_times[obj_id] = current_time

            duration = current_time - self.person_entry_times[obj_id]
            if obj_id in self.ignore_persons.keys():
                continue

            # detect fall
            if is_falling(x1, x2, y1, y2):
                print(f"Person {obj_id} is falling, position: {x1, y1, x2, y2}")
                event_id = str(uuid.uuid4())
                video, video_frames = await self.create_video(frame_id - 50, frame_id, obj_id, event_id)
                events.append(FallEvent(url=video, timestamp=get_formatted_now(), id=event_id))
                self.event_cache.append(EventCache(event_id=event_id, person_id=obj_id, frames_left=10, video_frames=video_frames))
                self.ignore_person_for(obj_id, 10)

            # detect prolonged time in frame
            if duration > 10:
                event_id = str(uuid.uuid4())
                video, video_frames = await self.create_video(frame_id - 50, frame_id, obj_id, event_id)
                events.append(ProlongedTimeEvent(url=video, timestamp=get_formatted_now(), id=event_id))
                self.event_cache.append(EventCache(event_id=event_id, person_id=obj_id, frames_left=10, video_frames=video_frames))
                self.ignore_person_for(obj_id, 20)

            self.person_durations[obj_id] = duration

        # remove historical data older than 180 seconds
        self.remove_expired_history(180)
        self.check_people_ignored()
        await self.process_events(image, objects)

        return ProcessorResult(
            events=events,
            objects=objects,
        )

    async def process_image(self, base64_img: str) -> ProcessorResult:
        image_data = base64.b64decode(base64_img)
        image = Image.open(io.BytesIO(image_data))

        result = await self.process_frame(image)

        try:
            for event in result.events:
                EventTable.create_event(event)
        except:
            traceback.print_exc()

        return result
