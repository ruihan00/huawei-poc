import asyncio

import asyncio
from google.cloud import storage


EVENTS_BUCKET_NAME = "huawei-binacloud-events"

from datetime import datetime

async def async_upload_blob(content: bytes, content_type=None) -> str:
    """Upload a file with a random name, returning URL"""
    client = storage.Client()
    bucket = client.bucket(EVENTS_BUCKET_NAME)

    name = datetime.now().strftime("%Y%m%d_%H%M%S")
    bucket_blob = bucket.blob(name)

    # Use asyncio.to_thread to run blocking operation in a separate thread
    await asyncio.to_thread(bucket_blob.upload_from_string, content, content_type)

    url = f"https://storage.googleapis.com/{EVENTS_BUCKET_NAME}/{name}"
    return url


if __name__ == "__main__":
    content = f"Hello world #".encode()
    output = asyncio.run(async_upload_blob(content))
    print(output)
