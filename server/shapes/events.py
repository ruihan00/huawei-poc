from enum import Enum
from pydantic import BaseModel
import time
class EventType(str, Enum):
    FALL = "Fall"
    PROLONGED_TIME = "Prolonged Time"
    MOBILITY_AID = "Mobility Aid"

class Event(BaseModel):
    type: EventType
    url: str
    timestamp: str
    id: str

class FallEvent(Event):
    type: EventType = EventType.FALL

class ProlongedTimeEvent(Event):
    type: EventType = EventType.PROLONGED_TIME

class MobilityAidEvent(Event):
    type: EventType = EventType.MOBILITY_AID
    name: str

class ReceiverImageEvent(BaseModel):
    id: str
    image: str

class ReceiverEventEvent(BaseModel):
    events: list[Event]


class EventCache(BaseModel):
    event_id: str
    person_id: str
    expiry: float
    video_frames: list