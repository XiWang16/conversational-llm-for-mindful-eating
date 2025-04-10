# media_uploader.py
from google.cloud import storage
import uuid
import mimetypes
import os
from urllib.parse import urlparse
from config import GCP_CREDENTIALS_PATH

class MediaUploader:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.client = storage.Client.from_service_account_json(GCP_CREDENTIALS_PATH)
        self.bucket = self.client.get_bucket(bucket_name)

    def upload_media_bytes(self, media_bytes, source_url=None, destination_blob_name=None, content_type="auto"):
        """
        Upload media content provided as bytes to GCS and return the public URL.

        - If `destination_blob_name` is not provided, generate a UUID-based name.
        - If `content_type` is "auto", detect it using `source_url` (e.g., from a file extension like .mp4).
        """
        # Guess file extension and MIME type if needed
        if destination_blob_name is None:
            ext = ""
            if source_url:
                parsed_path = urlparse(source_url).path
                ext = os.path.splitext(parsed_path)[1]  # includes the dot
            destination_blob_name = f"{uuid.uuid4()}{ext}"

        if content_type == "auto":
            content_type, _ = mimetypes.guess_type(destination_blob_name)
            if not content_type:
                content_type = "application/octet-stream"  # default fallback

        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(media_bytes, content_type=content_type)
        blob.make_public()

        print(f"✅ Uploaded {destination_blob_name} with content-type: {content_type}")
        return blob.public_url

    def upload_media_file(self, file_path, destination_blob_name=None):
        """
        Upload a media file from disk to GCS.
        """
        if destination_blob_name is None:
            destination_blob_name = str(uuid.uuid4())
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        blob.make_public()
        return blob.public_url
