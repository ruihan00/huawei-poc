from datetime import datetime
import base64
import json

import io
from PIL import Image, ImageDraw, ImageFont

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from shapes.sender_message import SenderMessage
from utils.image_processor import process_image
from logger import logger

router = APIRouter(prefix="/server")
senders = {}
receivers = []

@router.get("/healthcheck")
async def healthcheck():
    return {"message": "CCTV System Server is Running"}

fmt = lambda time: time.strftime("%H%M%S") + f".{time.microsecond // 1000:03d}"

@router.websocket("/sender")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    host = ws.client.host

    senders[ws.client.host] = ws
    logger.info(f"Sender {host} connected")

    try:
        while True:
            message = SenderMessage(**(await ws.receive_json()))
            logger.debug(f"Received data from {host}")

            # Remove "data:image/webp;base64,"
            base64_img = message.image.split(",")[1]

            request_time = datetime.fromisoformat(message.timestamp).replace(
                tzinfo=None
            )  # JS Date is tz-aware

            image_data = base64.b64decode(base64_img)
            image = Image.open(io.BytesIO(image_data))
            now = datetime.now()
            time = now.strftime("%H%M%S") + f".{now.microsecond // 1000:03d}"
            image.save(f"files/{fmt(request_time)}---{fmt(datetime.now())}.png")

            response = await process_image(base64_img)
            response.timestamp = message.timestamp
            for receiver in receivers:
                logger.debug(f"Sending data to receiver {host}")
                await receiver.send_text(response.model_dump_json())

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
