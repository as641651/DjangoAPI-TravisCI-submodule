from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


# sample user for the tests
def sample_user(email="test@test.com", password="testpass"):
    return get_user_model().objects.create(email=email, password=password)


class RecipeModelTests(TestCase):

    # test the tag usage
    def test_recipe_str(self):
        # only include mandatory fields here
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Wheat pizza",
            time_miniutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)
