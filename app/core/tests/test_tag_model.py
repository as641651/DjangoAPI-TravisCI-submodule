from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


# sample user for the tests
def sample_user(email="test@test.com", password="testpass"):
    return get_user_model().objects.create(email=email, password=password)


class TagModelTests(TestCase):

    # test the tag usage
    def test_tag_str(self):
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Vegan"
        )

        self.assertEqual(str(tag), tag.name)
