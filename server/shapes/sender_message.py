from pydantic import BaseModel

from models.model import ModelResult


class SenderMessage(BaseModel):
    timestamp: str
    image: str

class ReceiverMessage(BaseModel):
    # image: str
    # NOTE: If needed, create a something like FinalResult to decouple from ModelResult
    objects: list[ModelResult]
    timestamp: str = None  # Pass original timestamp back to client
