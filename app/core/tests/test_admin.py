from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):

    # Setup function is run before every test
    # create a super user, log him in and create a normal user
    def setUp(self):
        """Create a super user and log him in
            Create a user"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='aravind@gmail.com',
            password='1234'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='silent@retreat.com',
            password='1234',
            name='Test user name'
        )

    def test_users_listed(self):
        """Test that users are listed in user page.
        We have to make changes to django admin to accomodate
        ou custom user model"""

        # These urls are listed in django admin docs
        # Gets the URL that lists users in admin page
        # have to register User model to admin for this url to work
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        # AssertContains checks if certain value is present in a dict
        # Also checks if the http respose is OK (200)
        # name field is not available in default UserAdmin class
        self.assertContains(response, self.user.name)

    def test_user_page_change(self):
        """ Test that user edit page works"""

        # We have to include fieldssets to UserAdmin for this to work
        url = reverse('admin:core_user_change', args=[self.user.id])
        # /admin/core/user/1
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        url = reverse('admin:core_user_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
