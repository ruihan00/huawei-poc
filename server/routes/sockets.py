import collections
from datetime import datetime
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from shapes.messages import ReceiverAckMessage, ReceiverProcessedMessage, ReceiverImageMessage, ReceiverMessage, SenderMessage
from processor import Processor
from utils.image import strip_base64_prefix
from utils.logger import logger

from utils.external.firestore import EventTable
import uuid

router = APIRouter(prefix="/server")

window_size = 100
times = collections.deque(maxlen=window_size)


class Endpoint:
    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.host = ws.client.host

    async def receive_text(self, ack=True):
        start = time.time()
        data = await self.ws.receive_text()
        if ack:
            await self.send_text(ReceiverAckMessage().model_dump_json())
        end = time.time()
        return data, (end - start)


    async def receive_json(self, ack=True):
        start = time.time()
        data = await self.ws.receive_json()
        if ack:
            await self.send_text(ReceiverAckMessage().model_dump_json())
        end = time.time()
        return data, (end - start)

    async def send_text(self, text):
        start = time.time()
        await self.ws.send_text(text)
        end = time.time()
        return end - start

    async def send_json(self, text):
        start = time.time()
        await self.ws.send_json(text)
        end = time.time()
        return end - start

class Sender(Endpoint):
    def __init__(self, ws):
        super().__init__(ws)
        self.id = str(uuid.uuid4())

class Receiver(Endpoint):
    def __init__(self, ws):
        super().__init__(ws)


senders: dict[str, Sender] = {}
receivers: list[Receiver] = []


async def broadcast(message: ReceiverMessage):
    start = time.time()
    for receiver in receivers:
        await receiver.send_text(message.model_dump_json())
    end = time.time()
    return end - start


@router.websocket("/sender")
async def sender(ws: WebSocket):
    await ws.accept()

    sender = Sender(ws)

    senders[sender.id] = sender
    logger.info(f"Sender {sender.host} connected")

    processor = Processor()

    try:
        while True:
            sending_time = receiving_time = compute_time = 0

            # 1. Receive image from sender
            json_message, duration = await sender.receive_json()
            receiving_time += duration
            message = SenderMessage(**(json_message))
            img = message.image
            duration = await broadcast(ReceiverImageMessage(image=img, id=sender.id))
            sending_time += duration


            # 2. Compute
            results = None
            try:
                results, duration = await processor.process_image(strip_base64_prefix(message.image))
                compute_time += duration
            except Exception as e:
                logger.error(f"Error processing image: {e}")

            # 3. Send results to receiver
            if results is not None:
                duration = await broadcast(ReceiverProcessedMessage(events=results.events, objects=results.objects))
                sending_time += duration

            # 4. Compute stats
            # Latency
            request_time = datetime.fromisoformat(message.timestamp).replace(
                tzinfo=None
            )  # JS Date is tz-aware
            response_time = datetime.now()
            logger.debug(f"Response latency: {response_time - request_time}")

            # Profiling
            times.append((sending_time, receiving_time, compute_time))
            # Calculate the Simple Moving Average over the window size
            sending_sma = sum(time[0] for time in times) / window_size
            receiving_sma = sum(time[1] for time in times) / window_size
            compute_sma = sum(time[2] for time in times) / window_size
            total_sma = sending_sma + receiving_sma + compute_sma
            logger.debug("Profiling: " + " ".join([
                f"Sending {sending_sma:.3f}s ({sending_sma / total_sma:.3%})",
                f"Receiving {receiving_sma:.3f}s ({receiving_sma / total_sma:.3%})",
                f"Compute {compute_sma:.3f}s ({compute_sma / total_sma:.3%})"
            ]))

    except WebSocketDisconnect:
        senders.pop(sender.id, None)
        logger.info(f"Sender {sender.host}(id={sender.id}) disconnected")


@router.websocket("/receiver")
async def receiver(ws: WebSocket):
    await ws.accept()
    receiver = Receiver(ws)

    receivers.append(ws)
    logger.info(f"Receiver {receiver.host} connected")

    try:
        while True:
            await receiver.receive_text()

    except WebSocketDisconnect:
        receivers.remove(ws)
        logger.info(f"Receiver {receiver.host} disconnected")
