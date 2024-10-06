from datetime import datetime
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from shapes.sender_message import SenderMessage, ReceiverImageEvent, ReceiverMessage, ReceiverEventType, ReceiverEventEvent
from utils.image_processor import process_image
from logger import logger

router = APIRouter(prefix="/server")
senders = {}
receivers = []

@router.get("/healthcheck")
async def healthcheck():
    return {"message": "CCTV System Server is Running"}


async def broadcast(message: ReceiverMessage):
    for receiver in receivers:
        
        await receiver.send_text(message.json())

@router.websocket("/sender")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    host = ws.client.host

    senders[ws.client.host] = ws
    logger.info(f"Sender {host} connected")

    try:
        while True:
            message = SenderMessage(**(await ws.receive_json()))
            # Acknowledge receipt
            await ws.send_text(json.dumps({"message": "Received"}))
            # Remove "data:image/webp;base64,"
            img = message.image
            base64_img = message.image.split(",")[1]

            image_event = ReceiverImageEvent(image=img)
            receiver_message = ReceiverMessage(
                type=ReceiverEventType.IMAGE, data=image_event
            )
            await broadcast(receiver_message)
            events = []
            try:
                events = await process_image(base64_img)
            except Exception as e:
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
        senders.pop(ws.client.host, None)
        logger.info(f"Sender {ws.client.host} disconnected")


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
