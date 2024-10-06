import asyncio

import asyncio
from google.cloud import storage


EVENTS_BUCKET_NAME = "huawei-binacloud-events"

# [START storage_async_upload]
# This sample can be run by calling `async.run(async_upload_blob('bucket_name'))`
async def async_upload_blob(name: str, content: bytes, content_type=None):
    """Uploads a number of files in parallel to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    client = storage.Client()
    bucket = client.bucket(EVENTS_BUCKET_NAME)

    bucket_blob = bucket.blob(name)

    # Use asyncio.to_thread to run blocking operation in a separate thread
    await asyncio.to_thread(bucket_blob.upload_from_string, content, content_type)

    print(f"Uploaded files to bucket")



if __name__ == "__main__":
    blob_name = f"async_ample_blob"
    content = f"Hello world #".encode()
    asyncio.run(async_upload_blob(blob_name, content))
