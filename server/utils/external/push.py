import asyncio

import asyncio
from google.cloud import storage


EVENTS_BUCKET_NAME = "huawei-binacloud-events"

from datetime import datetime

async def async_upload_blob(content: bytes, content_type=None, filename: str ="") -> str:
    """Upload a file with a random name, returning URL"""
    client = storage.Client()
    bucket = client.bucket(EVENTS_BUCKET_NAME)

    bucket_blob = bucket.blob(filename)

    # Use asyncio.to_thread to run blocking operation in a separate thread
    await asyncio.to_thread(bucket_blob.upload_from_string, content, content_type)

    url = f"https://storage.googleapis.com/{EVENTS_BUCKET_NAME}/{filename}"
    return url


if __name__ == "__main__":
    content = f"Hello world #".encode()
    output = asyncio.run(async_upload_blob(content))
    print(output)
