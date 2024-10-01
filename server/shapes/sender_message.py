from pydantic import BaseModel


class SenderMessage(BaseModel):
    timestamp: str
    image: str

class ReceiverMessage(BaseModel):
    image: str
    timestamp: str = None  # Pass original timestamp back to client
