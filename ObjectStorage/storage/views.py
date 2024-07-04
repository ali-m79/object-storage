from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Object, User
from .services.s3_service import S3Service
from .services.file_upload_service import FileUploadService
from .services.email_service import EmailService
from .services.user_service import UserService

import math

class UploadObjectView(LoginRequiredMixin, View):
    """Handles file upload by authenticated users."""
    login_url = '/users/login/'

    def post(self, request):
        """Handles POST requests to upload files."""
        files = request.FILES.getlist('file')

        s3_service = S3Service()
        file_upload_service = FileUploadService(s3_service)

        try:
            for file in files:
                file_upload_service.upload_file(request.user, file)
            messages.success(request, 'File uploaded successfully.')
        except Exception as exc:
            messages.error(request, 'An error occurred while uploading the file.')

        return redirect('main')


class ObjectStorageView(LoginRequiredMixin, View):
    """Displays user's objects with search and pagination."""
    login_url = '/users/login/'

    def get(self, request):
        """Handles GET requests to display objects."""
        user = request.user

        owned_objects = Object.objects.filter(owner=user)
        accessible_objects = Object.objects.filter(access_users=user)
        objects = (owned_objects | accessible_objects).distinct()

        # Calculate total size of all objects
        total_size = sum(obj.size for obj in objects)
        total_size_readable = self.convert_size(total_size)

        # Perform search if query parameter is present
        query = request.GET.get('search', '')
        if query:
            objects = objects.filter(name__icontains=query)

        objects = objects.order_by('-upload_date')

        # Pagination setup
        paginator = Paginator(objects, 24)
        page_number = request.GET.get('page')
        page_objects = paginator.get_page(page_number)

        return render(request, 'main.html', {
            'objects': page_objects,
            'user': user,
            'total_size': total_size_readable,
        })

    @staticmethod
    def convert_size(size_bytes):
        """Converts bytes to a human-readable string."""
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"


class DeleteObjectView(LoginRequiredMixin, View):
    """Handles deletion of user's objects."""
    login_url = '/users/login/'

    def get(self, request, obj_id):
        """Handles GET requests to delete an object."""
        obj = get_object_or_404(Object, id=obj_id, owner=request.user)

        # Check ownership before deletion
        if obj.owner != request.user:
            messages.error(request, 'You have no permission to delete this file.')
            return redirect('main')

        s3_service = S3Service()

        try:
            s3_service.delete_file(obj.name)
            obj.delete()
            messages.success(request, 'File deleted successfully.')
        except Exception as exc:
            messages.error(request, 'An error occurred while deleting the file.')

        return redirect('main')


class DownloadObjectView(LoginRequiredMixin, View):
    """Handles file download requests."""
    login_url = '/users/login/'

    def get(self, request, obj_id):
        """Handles GET requests to download an object."""
        obj = get_object_or_404(Object, id=obj_id)

        # Check if user has permission to download
        if obj.owner != request.user and request.user not in obj.access_users.all():
            messages.error(request, 'You do not have permission to download this file.')
            return redirect('main')

        s3_service = S3Service()

        try:
            presigned_url = s3_service.generate_presigned_url(obj.name, expiration=3600)
            return redirect(presigned_url)

        except Exception as exc:
            messages.error(request, 'An error occurred while generating the download link.')
            return redirect('main')


class PopupView(LoginRequiredMixin, View):
    """Displays a popup with users and their access to an object."""
    login_url = '/users/login/'

    def get(self, request, obj_id):
        """Handles GET requests to display popup content."""
        obj = get_object_or_404(Object, id=obj_id)

        # Fetch users with and without access to the object
        users_with_access = UserService.get_users_with_access(obj)
        users_without_access = UserService.get_users_without_access(obj, request.user)

        # Format users for display in the popup
        users = UserService.format_users(users_with_access, True)
        users += UserService.format_users(users_without_access, False)

        return render(request, 'popup.html', {'users': users, 'object': obj_id})


class UpdateAccessUsersView(LoginRequiredMixin, View):
    """Handles updating access users for an object."""
    login_url = '/users/login/'

    def post(self, request, obj_id):
        """Handles POST requests to update access users."""
        obj = get_object_or_404(Object, id=obj_id)
        selected_users = request.POST.getlist('users')

        self.update_access_list(obj, selected_users)
        obj.save()  # Save the object to update the access list

        messages.success(request, 'Access users updated successfully.')
        return redirect('main')

    def update_access_list(self, obj, selected_users):
        """Clears and updates the access users list for the object."""
        # Clear current access users
        obj.access_users.clear()

        # Add selected users to access list and send notification emails
        for username in selected_users:
            user = get_object_or_404(User, username=username)
            obj.access_users.add(user)

            # Example: Send email to the user
            EmailService.send_email(
                subject='Access Granted to Object',
                template_name='access_email.html',
                context={'user': user, 'object': obj},
                recipient_list=[user.email]
            )
