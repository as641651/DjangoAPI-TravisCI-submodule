from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    # new user creation
    def test_create_user_with_email_successful(self):
        email = 'silent@retreat.com'
        password = '1234'

        # get_user_model() returns the default user model.
        # If it has to return custom usermodel, create a new models
        # and in settings.py Set AUTH_USER_MODEL pointing to custom model
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    # checking case sensitive email
    def test_new_user_email_normalized(self):
        """we want email field to be unique for users
        But the second part of the email address is Case sensitive by Default
        ie, xyz@gmail.com and xyz@GMAIL.COM will be unique values
        So we change email to lower case"""

        email = "test@ABC.COM"
        user = get_user_model().objects.create_user(email, '1234')

        self.assertEqual(user.email, email.lower())

    # check if invalid Email raises ValueError
    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '1234')

    # check if super user can be created
    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            'aravind@gmail.com',
            '1234'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
