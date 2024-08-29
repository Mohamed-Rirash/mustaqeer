import uuid
from fastapi import UploadFile, UploadFile, File, HTTPException, status, FastAPI

KB = 1024
MB = 1024 * KB

SUPPORTED_IMAGE_FORMATS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
import magic
import boto3

AWS_S3_BUCKET_NAME = "mustaqeer-profile"

s3 = boto3.resource("s3")
bucket = s3.Bucket(AWS_S3_BUCKET_NAME)

async def s3_upload(content: bytes, filename: str, content_type: str):
    bucket.put_object(Key=filename, Body=content, ContentType=content_type)

app = FastAPI()


@app.post("/upload-profile-image")
async def upload_profile_image(profile_image: UploadFile = File(...)):
    if not profile_image:
        raise HTTPException(status_code=400, detail="No profile image provided")
    content = await profile_image.read()
    size = len(content)
    if size > 1 * MB:
        raise HTTPException(status_code=400, detail="Profile image is too large")
    format = profile_image.content_type
    if format not in SUPPORTED_IMAGE_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported image format")
    file_type = magic.from_buffer(content, mime=True)
    if file_type not in SUPPORTED_IMAGE_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported image format")
    file_extension = SUPPORTED_IMAGE_FORMATS[format]
    filename = f"{uuid.uuid4()}.{SUPPORTED_IMAGE_FORMATS[file_type]}"
    await s3_upload(content=content, filename=filename, content_type=format)
    return {"message": "Profile image uploaded successfully"}
