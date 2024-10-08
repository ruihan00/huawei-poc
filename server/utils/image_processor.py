import base64
import io
import traceback

from PIL import Image

from utils.tracking import ProcessorResult, process_frame

from utils.external.firestore import EventTable

DOWNSCALE = None

async def process_image(base64_img: str) -> ProcessorResult:
    image_data = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(image_data))

    result = await process_frame(image)

    try:
        for event in result.events:
            EventTable.create_event(event)
    except:
        traceback.print_exc()

    return result
