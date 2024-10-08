from enum import Enum
from pydantic import BaseModel

class EventType(Enum):
    FALL = "Fall"
    PROLONGED_TIME = "Prolonged Time"

class Event(BaseModel):
    type: EventType
    url: str
    timestamp: str
    id: str

class FallEvent(Event):
    type: EventType = EventType.FALL

class ProlongedTimeEvent(Event):
    type: EventType = EventType.PROLONGED_TIME

class ReceiverImageEvent(BaseModel):
    id: str
    image: str

class ReceiverEventEvent(BaseModel):
    events: list[Event]
