import boto3
from fastapi import HTTPException, status
from app.config.settings import settings


KB = 1024
MB = 1024 * KB

SUPPORTED_IMAGE_FORMATS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

s3_client = boto3.resource("s3", aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

bucket = s3_client.Bucket(settings.AWS_S3_BUCKET_NAME)

async def s3_upload(content: bytes, filename: str, content_type: str):
    bucket.put_object(Key=filename, Body=content, ContentType=content_type)


async def delete_s3_image(filename):
    try:
        # Specify the bucket name (ensure settings.AWS_S3_BUCKET_NAME is defined)
        bucket_name = settings.AWS_S3_BUCKET_NAME

        # Delete the object from S3
        response = bucket.delete_objects(
            Delete={
                'Objects': [
                    {
                        'Key': filename
                    }
                ]
            }
        )

        # Optionally, check if the delete was successful (e.g., check response code)
        if response['ResponseMetadata']['HTTPStatusCode'] == 204:
            print(f"Successfully deleted {filename} from {bucket_name}")
        else:
            print(f"Failed to delete {filename} from {bucket_name}, response: {response}")

    except Exception as e:
        # Handle any errors that occur during the deletion process
        print(f"Error occurred while trying to delete {filename} from S3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting image from S3")
