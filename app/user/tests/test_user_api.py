from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


# 'Public' because we dont check for authentication
class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    # test API call to create new user
    def test_create_valid_user_success(self):
        """test creating user with valid payload
        payload is a POST dict"""

        payload = {
            'email': 'test@test.com',
            'password': 'testpass'
        }

        # This call to API should create a new user
        res = self.client.post(CREATE_USER_URL, payload)

        # assert if the response is 201 created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # get this user and check if password is correct
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        # assert that the password is not returned in the response data
        self.assertNotIn('password', res.data)

    # Test api when trying to create existing users
    def test_user_exists(self):
        # Note, the users created in previous test cases do not exist
        payload = {'email': 'test@test.com', 'password': 'testpass'}
        # create this user
        create_user(**payload)

        # try to create this user again with APIClient
        res = self.client.post(CREATE_USER_URL, payload)
        # assert that the response is 400
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test if user is not created when password is too short
    def test_password_too_short(self):
        # Note, the users created in previous test cases do not exist
        payload = {'email': 'test@test.com', 'password': 'tp'}
        res = self.client.post(CREATE_USER_URL, payload)

        # assert response failed
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # assert user was not created
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
