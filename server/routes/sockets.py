from datetime import datetime
import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from shapes.sender_message import SenderMessage, ReceiverImageEvent, ReceiverMessage, ReceiverEventType, ReceiverEventEvent
from utils.image_processor import process_image
from logger import logger

from utils.external.firestore import EventTable
import uuid
router = APIRouter(prefix="/server")
senders = {}
receivers = []

@router.get("/healthcheck")
async def healthcheck():
    return {"message": "CCTV System Server is Running"}


async def broadcast(message: ReceiverMessage):
    for receiver in receivers:
        await receiver.send_text(message.model_dump_json())

@router.websocket("/sender")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    host = ws.client.host
    host_id = str(uuid.uuid4())
    senders[host_id] = ws
    logger.info(f"Sender {host} connected")

    try:
        while True:
            message = SenderMessage(**(await ws.receive_json()))
            # Acknowledge receipt
            await ws.send_text(json.dumps({"message": "Received"}))
            # Remove "data:image/webp;base64,"
            img = message.image
            base64_img = message.image.split(",")[1]

            image_event = ReceiverImageEvent(image=img, id=host_id)
            receiver_message = ReceiverMessage(
                type=ReceiverEventType.IMAGE, data=image_event
            )
            await broadcast(receiver_message)
            events = []
            try:
                events = await process_image(base64_img)
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                pass
            if len(events) > 0:
                event_event = ReceiverEventEvent(events=events)
                receiver_message = ReceiverMessage(
                    type=ReceiverEventType.EVENT, data=event_event
                )
                await broadcast(receiver_message)
            request_time = datetime.fromisoformat(message.timestamp).replace(
                tzinfo=None
            )  # JS Date is tz-aware
            response_time = datetime.now()
            logger.debug(f"Response latency: {response_time - request_time}")

    except WebSocketDisconnect:
        senders.pop(host_id, None)
        logger.info(f"Sender {host_id} disconnected")


@router.websocket("/receiver")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    host = ws.client.host

    receivers.append(ws)
    logger.info(f"Receiver {host} connected")

    try:
        while True:
            data = await ws.receive_text()

    except WebSocketDisconnect:
        receivers.remove(ws)
        logger.info(f"Receiver {host} disconnected")


@router.get("/events")
async def get_events(id: Optional[int] = None):
    if id:
        return EventTable.get_event_by_id(id)
    else:
        return EventTable.get_events()
