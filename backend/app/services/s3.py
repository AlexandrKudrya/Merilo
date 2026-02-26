import uuid

import aiobotocore.session

from app.core.config import settings


async def upload_photo(file_bytes: bytes, content_type: str) -> str:
    """Upload photo to S3 and return the public URL."""
    key = f"receipts/{uuid.uuid4()}.jpg"

    session = aiobotocore.session.get_session()
    async with session.create_client(
        "s3",
        region_name=settings.s3_region,
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    ) as client:
        await client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )

    return f"{settings.s3_endpoint_url}/{settings.s3_bucket_name}/{key}"
