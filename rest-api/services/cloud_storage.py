import base64
from typing import BinaryIO

from flask import Flask
from google.cloud import storage
from google.cloud.storage import Bucket

google_cloud_storage_url = "https://storage.googleapis.com"


class CloudStorageService(object):
    _instance = None
    client = None
    default_bucket = None

    def __init__(self):
        raise Exception(
            "call init_app(app) to initialize or instance() to get instance"
        )

    @classmethod
    def instance(cls):
        if cls._instance is None:
            raise Exception("Class has not been initialized")
        return cls._instance

    @classmethod
    def init_app(cls, app: Flask):
        if cls._instance is not None:
            app.logger.error("Attempted reinitialization of singlton OpenTokClient")
            return

        cls._instance = cls.__new__(cls)
        cls.client = storage.Client()
        cls.default_bucket = app.config.get("STORAGE_BUCKET")

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

    def upload_file(
        self,
        object_name: str,
        data: BinaryIO,
        data_size: int = 0,
        file_type: str = "application/octet-stream",
        bucket_name: str = None,
    ) -> str:
        if bucket_name is None:
            bucket_name = self.default_bucket

        bucket: Bucket = self.client.bucket(bucket_name)
        object_blob = bucket.blob(object_name)
        object_blob.upload_from_file(
            file_obj=data, content_type=file_type, size=data_size
        )

        return object_blob.public_url
