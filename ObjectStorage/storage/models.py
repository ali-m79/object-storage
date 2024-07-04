from django.db import models
from django.contrib.auth.models import User

class Object(models.Model):
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_objects'
    )
    file_url = models.URLField(max_length=255, blank=True)  # Added blank=True for optional URL
    name = models.CharField(max_length=255)
    size = models.BigIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    access_users = models.ManyToManyField(
        User, 
        related_name='accessible_objects', 
        blank=True
    )
    
    IMAGE = 'image'
    PDF = 'pdf'
    VIDEO = 'video'
    MUSIC = 'music'
    OTHER = 'other'
    
    FILE_TYPE_CHOICES = [
        (IMAGE, 'Image'),
        (PDF, 'PDF Document'),
        (VIDEO, 'Video'),
        (MUSIC, 'Music'),
        (OTHER, 'Other'),
    ]
    
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default=OTHER,
    )

    def __str__(self):
        return self.name

    def add_access(self, user):
        """
        Adds access to the object for a user.

        Args:
            user (User): The user to grant access.

        Returns:
            None
        """
        self.access_users.add(user)

    def remove_access(self, user):
        """
        Removes access to the object for a user.

        Args:
            user (User): The user to remove access from.

        Returns:
            None
        """
        self.access_users.remove(user)
