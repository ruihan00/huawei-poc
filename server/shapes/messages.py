
from enum import Enum
from pydantic import BaseModel

from models.model import ModelObject
from shapes.events import Event

class SenderMessage(BaseModel):
    timestamp: str
    image: str

class ReceiverMessageType(Enum):
    IMAGE = "image"
    EVENTS = "events"
    ACK = "ack"

class ReceiverMessage(BaseModel):
    type: ReceiverMessageType

class ReceiverImageMessage(ReceiverMessage):
    type: ReceiverMessageType = ReceiverMessageType.IMAGE
    id: str
    image: str

class ReceiverProcessedMessage(ReceiverMessage):
    type: ReceiverMessageType = ReceiverMessageType.EVENTS
    events: list[Event]
    # Raw result from the Stage 1 model, for debugging purposes
    objects: list[ModelObject]

class ReceiverAckMessage(ReceiverMessage):
    type: ReceiverMessageType = ReceiverMessageType.ACK
