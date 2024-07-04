import boto3
from django.conf import settings

class S3Service:
    def __init__(self):
        self.client = self._get_client()
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def _get_client(self):
        """
        Creates and returns an S3 client instance using AWS credentials from Django settings.

        Returns:
            boto3.client: S3 client instance.
        """
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME,
        )

    def upload_file(self, file, bucket_name, file_name):
        """
        Uploads a file to S3.

        Args:
            file (File): The file to upload to the S3 bucket.
            bucket_name (str): The name of the S3 bucket to upload the file to.
            file_name (str): The name of the file in the S3 bucket."""

        self.client.upload_fileobj(file, bucket_name, file_name)

        return f"{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"
    



    def delete_file(self, file_name):
        """
        Deletes a file from S3.

        Args:
            file_name (str): The name of the file to delete from the S3 bucket.
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_name)
        except Exception as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")

    def generate_presigned_url(self, file_name, expiration=3600):
        """
        Generates a presigned URL for downloading a file from S3.

        Args:
            file_name (str): The name of the file in the S3 bucket.
            expiration (int): Expiration time in seconds for the presigned URL (default: 3600 seconds).

        Returns:
            str: The presigned URL.
        """
        try:
            response = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_name},
                ExpiresIn=expiration
            )
            return response
        except Exception as e:
            raise Exception(f"Failed to generate presigned URL for file from S3: {str(e)}")
