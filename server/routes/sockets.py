from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.image_processor import process_image
import json
from logger import logger
import base64
import asyncio

router = APIRouter()
senders = {}
receivers = []

async def handle_frame(websocket_host: str, data: str):
    base64_str = data.split(",")[1]
    data = await process_image(base64_str)  # Ensure process_image is non-blocking or async if needed
    logger.debug(f"Received data from {websocket_host}")
    
    client_packet = {
        "camera_id": websocket_host,
        "image": data
    }
    
    for receiver in receivers:
        logger.debug(f"Sending data to receiver {receiver.client.host}")
        await receiver.send_text(json.dumps(client_packet))

@router.websocket("/ws/{client_type}")
async def websocket_endpoint(websocket: WebSocket, client_type: str):
    await websocket.accept()
    
    if client_type == "sender":
        senders[websocket.client.host] = websocket
        print(f"Sender {websocket.client.host} connected")
    elif client_type == "receiver":
        receivers.append(websocket)
        print(f"Receiver {websocket.client.host} connected")
    else:
        await websocket.close()
        return
    
    try:
        while True:
            if client_type == "sender":
                data = await websocket.receive_text()
                asyncio.create_task(handle_frame(websocket.client.host, data))
            else:
                data = await websocket.receive_text()
    
    except WebSocketDisconnect:
        if client_type == "sender":
            senders.pop(websocket.client.host, None)
            print(f"Sender {websocket.client.host} disconnected")
        elif client_type == "receiver":
            receivers.remove(websocket)
            print(f"Receiver {websocket.client.host} disconnected")
