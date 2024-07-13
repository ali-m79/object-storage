import re
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from .tokens import account_activation_token

class RegisterView(View):
    def get(self, request):
        """Display the registration form."""
        return render(request, 'register.html')

    def post(self, request):
        """Handle registration form submission."""
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')

        if not self.validate_registration(username, email, password, confirm_password):
            return redirect('register')

        try:
            user = self.create_user(username, email, password)
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return redirect('register')

        self.send_activation_email(user, request)
        request.session['email'] = email
        return redirect('active')

    def validate_registration(self, username, email, password, confirm_password):
        """Validate user registration inputs."""
        if password != confirm_password:
            messages.error(self.request, 'Passwords do not match.')
            return False

        if len(username) < 4 or not re.match("^[A-Za-z]*$", username):
            messages.error(self.request, 'Username must be at least 4 characters and contain only English letters.')
            return False

        if len(password) < 6 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"[0-9]", password) or not re.search(r"[!@#$%&]", password):
            messages.error(self.request, 'Password must be at least 6 characters, including one number, one special character (!@#$%&), one uppercase, and one lowercase letter.')
            return False

        if User.objects.filter(username=username).exists():
            messages.error(self.request, 'Username already exists.')
            return False

        if User.objects.filter(email=email).exists():
            messages.error(self.request, 'Email already exists.')
            return False
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(self.request, 'Enter a valid email address.')
            return False

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(self.request, 'Enter a valid email address.')

        return True

    def create_user(self, username, email, password):
        """Create a new user."""
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  # User is inactive until activation
        user.save()
        return user

    def send_activation_email(self, user, request):
        """Send activation email with activation link."""
        mail_subject = 'Activate your account'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_link = request.build_absolute_uri(
            reverse('activate', kwargs={'uidb64': uid, 'token': token})
        )
        message = render_to_string('email_activation.html', {
            'user': user,
            'activation_link': activation_link,
        })
        email = EmailMessage(subject=mail_subject, body=message, to=[user.email])
        email.send()


class ActivePageView(TemplateView):
    template_name = 'active.html'

    def get(self, request):
        """Display the active page."""
        email = request.session.get('email')
        if not email:
            return redirect('register')

        del request.session['email']
        return self.render_to_response({"email": email})


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        """Activate user account based on activation link."""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been activated.')
            return redirect('login')
        else:
            messages.error(request, 'Activation link is invalid!')
            return redirect('register')


class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        """Display the login form."""
        return render(request, self.template_name)

    def post(self, request):
        """Handle login form submission."""
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        user = self.authenticate_user(username_or_email, password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('main')  # Redirect to the home page or any other page
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, self.template_name)

    def authenticate_user(self, username_or_email, password):
        """Authenticate user based on username or email."""
        if re.match(r"[^@]+@[^@]+\.[^@]+", username_or_email):
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                username = None
        else:
            username = username_or_email

        return authenticate(self.request, username=username, password=password)


class LogoutView(View):
    def get(self, request):
        """Handle user logout."""
        logout(request)
        return redirect('login')
