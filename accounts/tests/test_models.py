from django.test import TestCase
from django.contrib import auth
from django.forms import ValidationError
from accounts.models import Token
User = auth.get_user_model()


class UserModelTest(TestCase):
        
    def test_email_is_primary_key(self):
        user = User(email='a@b.com')
        self.assertEqual(user.pk, 'a@b.com')
        
    def test_no_problem_with_auth_login(self):
        user = User.objects.create(email='edith@example.com')
        user.backend = ''
        request = self.client.request().wsgi_request
        auth.login(request, user) # should not raise
        
        
class TokenModelTest(TestCase):

    def test_links_user_with_auto_generated_uid(self):
        token1 = Token.objects.create(email='a@b.com')
        token2 = Token.objects.create(email='a@b.com')
        self.assertNotEqual(token1.uid, token2.uid)

        
class UserManagerTest(TestCase):

    def test_create_user_only_requires_email(self):
        user = User.objects.create_user('user@example.com')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user, User.objects.first())
        
    def test_create_user_sets_unusable_password(self):
        user = User.objects.create_user('user@example.com')
        self.assertTrue(user.password)
        self.assertFalse(user.has_usable_password())
        
    def test_create_user_performs_validation(self):
        with self.assertRaises(ValidationError):
            User.objects.create_user('')

    def test_create_superuser_requires_email_and_password(self):
        with self.assertRaises(TypeError):
            User.objects.create_superuser('admin@example.com')
        User.objects.create_superuser('admin@example.com', 'testpassword')
        
    def test_create_superuser_creates_admins(self):
        superuser = User.objects.create_superuser('admin@example.com', 'testpassword')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(superuser, User.objects.first())
        self.assertTrue(User.objects.first().is_admin)
     
    def test_create_superuser_performs_validation(self):
        with self.assertRaises(ValidationError):
            User.objects.create_superuser('', '')
