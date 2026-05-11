from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class CoreAppTests(TestCase):
    def setUp(self):
        """Set up test data before each test method."""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='[EMAIL_ADDRESS]',
            password='password123'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='[EMAIL_ADDRESS]',
            password='password123'
        )

    def test_superuser_can_access_dashboard(self):
        """Test that a superuser can access the admin dashboard."""
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Site administration')
        self.assertContains(response, 'Logged in as admin')

    def test_regular_user_cannot_access_admin_dashboard(self):
        """Test that a regular user cannot access the admin dashboard."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)

    def test_login_required_for_dashboard(self):
        """Test that dashboard requires authentication."""
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{reverse("admin:login")}?next={reverse("admin:index")}')

    def test_admin_dashboard_logout(self):
        """Test the admin logout functionality."""
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('admin:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin:login'))
        self.assertContains(response, 'Logged out')

    def test_superuser_creation(self):
        """Test that a superuser can be created."""
        self.assertTrue(self.admin_user.is_active)
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.admin_user.is_superuser)

    def test_user_creation(self):
        """Test that a regular user can be created."""
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertIsNone(self.user.last_login)

    def test_unicode_representation(self):
        """Test the __str__ method for User model."""
        self.assertEqual(str(self.admin_user), 'admin')
        self.assertEqual(str(self.user), 'testuser')
