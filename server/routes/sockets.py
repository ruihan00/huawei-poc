from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.image_processor import process_image
from PIL import Image
import io
import json
from logger import logger
import base64
router = APIRouter()
senders = {}
receivers = []

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
                # convert to bytes
                base64_str = data.split(",")[1]

                data = process_image(base64_str)
                logger.debug(f"Received data from {websocket.client.host}")
                
                
                client_packet = {
                    "camera_id": websocket.client.host,
                    "image": data
                }
                
                for receiver in receivers:
                    logger.debug(f"Sending data to receiver {receiver.client.host}")
                    
                    await receiver.send_text(json.dumps(client_packet))

            else:
                data = await websocket.receive_text()
            
    
    except WebSocketDisconnect:
        if client_type == "sender":
            senders.pop(websocket.client.host, None)
            print(f"Sender {websocket.client.host} disconnected")
        elif client_type == "receiver":
            receivers.remove(websocket)
            print(f"Receiver {websocket.client.host} disconnected")
