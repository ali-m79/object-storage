from django.contrib.auth.models import User
from storage.models import Object
from django.conf import settings
import os
from datetime import datetime  

class FileUploadService:
    def __init__(self, s3_service):
        self.s3_service = s3_service

    def upload_file(self, user: User, file):
        """
        Uploads a file to AWS S3 and saves metadata to the database.

        Args:
            user (User): The user uploading the file.
            file (UploadedFile): The file object to upload.

        Raises:
            Exception: If there's an error during file upload or metadata save.
        """
        try:
            file_type = self._get_file_type(file.name)  # Determine file type based on file name
            print(file.name)
            # Check if the file already exists in the database
            existing_file = Object.objects.filter(name=file.name).first()
         




            if existing_file and existing_file.owner == user:
                # Update existing file metadata
                file_url = self.s3_service.upload_file(file, settings.AWS_STORAGE_BUCKET_NAME, file.name)
                self._update_file_metadata(existing_file)

            elif existing_file and not (existing_file.owner == user):
                # Save new file metadata with user id in the end of name
                file.name = file.name.replace(file.name.split('.')[-1], '') + '_' + str(user.id) + '.' + file.name.split('.')[-1]
                print(file.name)
                file_url = self.s3_service.upload_file(file, settings.AWS_STORAGE_BUCKET_NAME, file.name)
                self._save_file_metadata(user, file, file_url, file_type)

            else :
                # save with the orginal name
                file_url = self.s3_service.upload_file(file, settings.AWS_STORAGE_BUCKET_NAME, file.name)
                self._save_file_metadata(user, file, file_url, file_type)

        except Exception as e:
            raise Exception(f"Failed to upload file and save metadata: {str(e)}")

    def _get_file_type(self, filename):
        """
        Determines the file type based on the file name's extension.

        Args:
            filename (str): The name of the file.

        Returns:
            str: The type of the file ('image', 'pdf', 'video', 'music', 'other').
        """
        file_extension = os.path.splitext(filename)[1].lower()  # Get file extension and convert to lowercase
        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return 'image'
        elif file_extension == '.pdf':
            return 'pdf'
        elif file_extension in ['.mp4', '.avi', '.mkv', '.mov']:
            return 'video'
        elif file_extension in ['.mp3', '.wav', '.flac', '.aac']:
            return 'music'
        else:
            return 'other'

    def _save_file_metadata(self, user, file, file_url, file_type):
        """
        Saves file metadata to the database.

        Args:
            user (User): The user who uploaded the file.
            file (UploadedFile): The file object being uploaded.
            file_url (str): The URL of the file in AWS S3.
            file_type (str): The type of the file ('image', 'pdf', 'video', 'music', 'other').
        """
        try:
            Object.objects.create(
                owner=user,
                file_url=file_url,
                name=file.name,
                size=file.size,
                file_type=file_type,
            )
        except Exception as e:
            raise Exception(f"Failed to save file metadata: {str(e)}")

    def _update_file_metadata(self, existing_file):
        """
        Updates the upload date of an existing file in the database.

        Args:
            existing_file (Object): The existing file object to update.
        """
        try:
            existing_file.upload_date = datetime.now()
            existing_file.save()  # Save changes to update the datetime
        except Exception as e:
            raise Exception(f"Failed to update file metadata: {str(e)}")
