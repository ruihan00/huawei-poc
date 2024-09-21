import io
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.image_processor import process_image
import json
from logger import logger
import base64
import asyncio

router = APIRouter()
senders = {}
receivers = []


@router.websocket("/ws/sender")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    host = ws.client.host

    senders[ws.client.host] = ws
    logger.info(f"Sender {host} connected")

    try:
        while True:
            data = await ws.receive_text()
            logger.debug(f"Received data from {host}")
            base64_img = data.split(",")[1]
            b = await process_image(base64_img)

            for receiver in receivers:
                logger.debug(f"Sending data to receiver {host}")
                await receiver.send_bytes(b)

    except WebSocketDisconnect:
        senders.pop(ws.client.host, None)
        logger.info(f"Sender {ws.client.host} disconnected")

@router.websocket("/ws/receiver")
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
