from pydantic import BaseModel


class SenderMessage(BaseModel):
    timestamp: str
    image: str
