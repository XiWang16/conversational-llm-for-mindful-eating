# media_uploader.py
from google.cloud import storage
import uuid

class MediaUploader:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(bucket_name)

    def upload_media_bytes(self, media_bytes, destination_blob_name=None, content_type="auto"):
        """
        Upload media content provided as bytes to GCS and return the public URL.
        """
        if destination_blob_name is None:
            destination_blob_name = str(uuid.uuid4())
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(media_bytes, content_type=content_type)
        # Make the blob public so it can be accessed via URL
        blob.make_public()
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
