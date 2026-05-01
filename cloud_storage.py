from google.cloud import storage
import uuid
import os

BUCKET_NAME = "dsc333-food-tracker"

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

def upload_image_to_gcs(local_file_path):
    ext = os.path.splitext(local_file_path)[1]
    blob_name = f"{uuid.uuid4().hex}{ext}"

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_file_path)

    return f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"