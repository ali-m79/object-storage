from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from .models import Object

class ObjectStorageViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.object = Object.objects.create(name='testfile.txt', size=1024, owner=self.user)

    @patch('storage.views.S3Service')
    @patch('storage.views.FileUploadService')
    def test_upload_object(self, MockFileUploadService, MockS3Service):
        """Test successful file upload."""
        MockFileUploadService().upload_file.return_value = None

        # Create a temporary file for upload
        with open('testfile.txt', 'w') as f:
            f.write('Test file content')

        with open('testfile.txt', 'rb') as f:
            response = self.client.post(reverse('upload'), {'file': f})

        self.assertRedirects(response, reverse('main'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, 'File uploaded successfully.')
        self.assertEqual(messages[0].tags, 'success')

    @patch('storage.views.S3Service')
    def test_delete_object(self, MockS3Service):
        """Test successful file deletion."""
        response = self.client.get(reverse('delete', args=[self.object.id]))

        self.assertRedirects(response, reverse('main'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, 'File deleted successfully.')
        self.assertEqual(messages[0].tags, 'success')
        self.assertFalse(Object.objects.filter(id=self.object.id).exists())

    @patch('storage.views.S3Service')
    def test_download_object(self, MockS3Service):
        """Test successful file download."""
        MockS3Service().generate_presigned_url.return_value = 'http://example.com/download/testfile.txt'

        response = self.client.get(reverse('download', args=[self.object.id]))

        self.assertRedirects(response, 'http://example.com/download/testfile.txt',fetch_redirect_response=False)

    def test_popup_view(self):
        """Test popup view rendering."""
        response = self.client.get(reverse('popup', args=[self.object.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'popup.html')
        self.assertContains(response, 'users')

    @patch('storage.views.EmailService')
    def test_update_access_users(self, MockEmailService):
        """Test updating access users for an object."""
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        data = {'users': ['otheruser']}

        response = self.client.post(reverse('update_access_users', args=[self.object.id]), data)

        self.assertRedirects(response, reverse('main'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, 'Access users updated successfully.')
        self.assertEqual(messages[0].tags, 'success')
        self.assertIn(other_user, self.object.access_users.all())
        MockEmailService.send_email.assert_called_once()
