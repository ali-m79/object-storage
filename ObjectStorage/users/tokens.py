from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        """
        Generate a hash value using user's primary key, timestamp, and user's active status.

        Args:
        - user: User object for whom the token is generated.
        - timestamp: Timestamp of when the token is created.

        Returns:
        - str: Hash value used as part of the activation token.
        """
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()
