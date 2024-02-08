import base64

from google.cloud import storage

google_cloud_storage_url = "https://storage.googleapis.com"


class CloudStorageService(object):
    client = None
    default_bucket = None

    def __init__(self, storage_bucket: str):
        self.client = storage.Client()
        self.default_bucket = storage_bucket

    def upload_image(
        self,
        img_name: str,
        img_data: str,
        file_type: str,
        bucket_name: str = None,
    ) -> str:
        if bucket_name is None:
            bucket_name = self.default_bucket

        bucket = self.client.get_bucket(bucket_name)
        img_bytes = base64.b64decode(img_data)

        # Upload the profile picture to the Cloud Storage bucket
        blob = bucket.blob(img_name)
        blob.upload_from_string(img_bytes, content_type=file_type)

        return blob.public_url
