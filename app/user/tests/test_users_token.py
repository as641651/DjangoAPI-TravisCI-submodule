from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

TOKEN_URL = reverse("user:token")


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class UserTokenTests(TestCase):
    """The API client may not want to send users ID and password
        for every request. In such cases, the user may generate a token
        which will be used for authentication"""

    def setUp(self):
        self.client = APIClient()

    # test if token can be created successfully
    # with valid creds for existing user
    def test_create_token_for_user(self):
        payload = {'email': 'test@test.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # test if token cannot be created with invalid credentials
    def create_token_invalid_credentials(self):
        create_user(email='test@test.com', password='testpass')
        payload = {'email': 'test@test.com', 'password': 'wrong'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # test if token cannot be created for non existing user
    def create_token_no_user(self):
        payload = {'email': 'test@test.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # test if token is not created when a fied is left blank
    def create_token_missing_field(self):
        payload = {'email': 'test@test.com', 'password': 'testpass'}
        create_user(**payload)
        payload = {'email': 'test@test.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
