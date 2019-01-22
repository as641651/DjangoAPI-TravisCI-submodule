from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApiTests(TestCase):
    """ Test publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    # test if ingredients api required authentication
    def test_login_required(self):
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """ Test  private ingredients api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # test if ingredients can be retrieved
    def test_retrieve_ingredients_list(self):
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # test if ingredients returned are limited to the auth user
    def test_ingredients_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            "other@test.com",
            "testpass"
        )

        ingred = Ingredient.objects.create(user=self.user, name="auth user")
        Ingredient.objects.create(user=user2, name="other user")

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingred.name)

    # test ingredient creation api
    def test_create_ingredient_successful(self):
        payload = {'name': 'cucumber'}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    # test if invalid ingredients are not created
    def test_create_ingredient_invalid(self):
        res = self.client.post(INGREDIENT_URL, {'name': ''})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # retrieve ingredients assgned to recipes
    def test_retrieve_ingredients_assigned_to_recipes(self):
        ingredient1 = Ingredient.objects.create(user=self.user, name="apple")
        ingredient2 = Ingredient.objects.create(user=self.user, name="turkey")

        recipe = Recipe.objects.create(
            title="Apple crumble",
            time_miniutes=5,
            price=10.00,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
