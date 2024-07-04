from django.contrib.auth.models import User

class UserService:
    @staticmethod
    def get_users_with_access(obj):
        """
        Retrieves users who have access to the given object.

        Args:
            obj (Object): The Object instance to check access for.

        Returns:
            QuerySet: A queryset of User objects who have access.
        """
        return User.objects.filter(is_active=True, id__in=obj.access_users.values('id'))

    @staticmethod
    def get_users_without_access(obj, current_user):
        """
        Retrieves users who do not have access to the given object.

        Args:
            obj (Object): The Object instance to check access for.
            current_user (User): The current user who owns the object.

        Returns:
            QuerySet: A queryset of User objects who do not have access.
        """
        return User.objects.filter(is_active=True).exclude(id=current_user.id).exclude(id__in=obj.access_users.values('id'))

    @staticmethod
    def format_users(users, has_access):
        """
        Formats a list of User objects into a structured dictionary format.

        Args:
            users (QuerySet): QuerySet of User objects.
            has_access (bool): Indicates whether users have access to an object.

        Returns:
            list: A list of dictionaries containing 'username', 'email', and 'has_access'.
        """
        return [
            {
                'username': user.username,
                'email': user.email,
                'has_access': has_access
            }
            for user in users
        ]
