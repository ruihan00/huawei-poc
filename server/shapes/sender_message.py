from pydantic import BaseModel

from models.model import ModelResult
from enum import Enum
from typing import List
class SenderMessage(BaseModel):
    timestamp: str
    image: str


class ReceiverEventType(str, Enum):
    IMAGE = "image"
    EVENT = "event"

class ReceiverImageEvent(BaseModel):
    image: str

class Event(BaseModel):
    type: str
    url: str
    timestamp: str
    id: str

class ReceiverEventEvent(BaseModel):
    events: List[Event]

class ReceiverMessage(BaseModel):
    type: ReceiverEventType
    data: ReceiverImageEvent | ReceiverEventEvent
