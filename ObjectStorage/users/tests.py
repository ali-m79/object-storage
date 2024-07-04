from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core import mail
from .tokens import account_activation_token

class RegisterViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.valid_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'Password1!',
            'confirmpassword': 'Password1!'
        }

    def test_register_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_post_valid(self):
        response = self.client.post(self.register_url, self.valid_data)
        self.assertRedirects(response, reverse('active'))
        user = User.objects.get(username='testuser')
        self.assertFalse(user.is_active)

    def test_register_post_password_mismatch(self):
        data = self.valid_data.copy()
        data['confirmpassword'] = 'DifferentPassword!'
        response = self.client.post(self.register_url, data)
        self.assertRedirects(response, self.register_url)
        self.assertEqual(User.objects.filter(username='testuser').count(), 0)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, 'Passwords do not match.')

    def test_register_post_username_exists(self):
        User.objects.create_user(username='testuser', email='existinguser@example.com', password='Password1!')
        response = self.client.post(self.register_url, self.valid_data)
        self.assertRedirects(response, self.register_url)
        self.assertEqual(User.objects.filter(email='testuser@example.com').count(), 0)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, 'Username already exists.')

    def test_register_post_email_exists(self):
        User.objects.create_user(username='anotheruser', email='testuser@example.com', password='Password1!')
        response = self.client.post(self.register_url, self.valid_data)
        self.assertRedirects(response, self.register_url)
        self.assertEqual(User.objects.filter(username='testuser').count(), 0)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, 'Email already exists.')

    def test_register_post_weak_password(self):
        data = self.valid_data.copy()
        data['password'] = 'weak'
        data['confirmpassword'] = 'weak'
        response = self.client.post(self.register_url, data)
        self.assertRedirects(response, self.register_url)
        self.assertEqual(User.objects.filter(username='testuser').count(), 0)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, 'Password must be at least 6 characters, including one number, one special character (!@#$%&), one uppercase, and one lowercase letter.')

    def test_register_post_invalid_username(self):
        data = self.valid_data.copy()
        data['username'] = 'us'
        response = self.client.post(self.register_url, data)
        self.assertRedirects(response, self.register_url)
        self.assertEqual(User.objects.filter(email='testuser@example.com').count(), 0)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, 'Username must be at least 4 characters and contain only English letters.')

   

    def test_register_post_invalid_password(self):
        data = self.valid_data.copy()
        data['password'] = 'short'
        data['confirmpassword'] = 'short'
        response = self.client.post(self.register_url, data)
        self.assertRedirects(response, self.register_url)
        self.assertEqual(User.objects.filter(username='testuser').count(), 0)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, 'Password must be at least 6 characters, including one number, one special character (!@#$%&), one uppercase, and one lowercase letter.')

class ActivePageViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.active_url = reverse('active')
        self.session = self.client.session
        self.session['email'] = 'testuser@example.com'
        self.session.save()

    def test_active_get(self):
        response = self.client.get(self.active_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'active.html')

class ActivateAccountViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='Password1!')
        self.user.is_active = False
        self.user.save()
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        self.activate_url = reverse('activate', kwargs={'uidb64': uid, 'token': token})

    def test_activate_account_valid(self):
        response = self.client.get(self.activate_url)
        self.assertRedirects(response, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_account_invalid(self):
        invalid_uid = urlsafe_base64_encode(force_bytes(999))
        invalid_url = reverse('activate', kwargs={'uidb64': invalid_uid, 'token': 'invalid-token'})
        response = self.client.get(invalid_url)
        self.assertRedirects(response, reverse('register'))

class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='Password1!')

    def test_login_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_post_valid(self):
        response = self.client.post(self.login_url, {'username_or_email': 'testuser', 'password': 'Password1!'})
        self.assertRedirects(response, reverse('main'))

    def test_login_post_valid_with_email(self):
        response = self.client.post(self.login_url, {'username_or_email': 'testuser@example.com', 'password': 'Password1!'})
        self.assertRedirects(response, reverse('main'))

    def test_login_post_invalid(self):
        response = self.client.post(self.login_url, {'username_or_email': 'testuser', 'password': 'WrongPassword'})
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Invalid username or password')

class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='Password1!')
        self.client.login(username='testuser', password='Password1!')
        self.logout_url = reverse('logout')

    def test_logout(self):
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)
