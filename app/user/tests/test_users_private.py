from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

ME_URL = reverse("user:me")


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PrivateUsersApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@test.com',
            password='testpass',
            name='name'
        )

        self.client = APIClient()

    # test that authentication is required for users
    def test_retrieve_user_unautherized(self):
        """ Test that authentication is required for users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # Test retrieving profile for logged in user
    # Also test if the response contain the expected data
    def test_retrieve_profile_successful(self):
        # log in client
        self.client.force_authenticate(user=self.user)
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    # Test if post if not allowed in to this api
    def test_post_me_not_allowed(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # test update user profile
    def test_update_user_profile(self):
        self.client.force_authenticate(user=self.user)
        payload = {'name': 'new name', 'password': 'new pass'}
        # with patch you can just send the fields to be updated.
        # other fields wont be affected.
        # with PUT you have to send the entire record
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
