from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.conf import settings

class EmailService:
    @staticmethod
    def send_email(subject, template_name, context, recipient_list):
        """
        Sends an email using an HTML template.

        Args:
        - subject (str): Subject of the email.
        - template_name (str): Name of the template file (e.g., 'email_template.html').
        - context (dict): Context data to render the template.
        - recipient_list (list): List of recipient email addresses.

        Returns:
        - None

        Raises:
        - Any exceptions encountered during email sending.
        """
        try:
            # Load HTML template
            html_template = get_template(template_name)
            html_content = html_template.render(context)

            # Create plain text version by stripping HTML
            plain_content = strip_tags(html_content)

            # Send email using EmailMultiAlternatives for HTML support
            msg = EmailMultiAlternatives(subject, plain_content, settings.DEFAULT_FROM_EMAIL, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            # Handle exceptions here (e.g., log the error, notify admins, etc.)
            print(f"Failed to send email: {str(e)}")
