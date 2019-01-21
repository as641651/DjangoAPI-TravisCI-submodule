from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Ingredient, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# for image upload tests
import tempfile
import os
from PIL import Image


# recipies API for GET/POST list
# /api/recipe/recipes
RECIPES_URL = reverse("recipe:recipe-list")


# recipies API for GET/PUT/PATCH/DELETE Detail
# /api/recipe/recipes/1/
def detail_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


# recipies API to POST image (custom action)
# /api/recipe/recipes/1/upload-image
def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def sample_tag(user, name='main course'):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='sample ingredient'):
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **kwargs):
    """Create a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_miniutes': 10,
        'price': 5.00
    }
    defaults.update(kwargs)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """ Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """ Test authenticated recipe api access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    # test retrieval of list of recipies
    def test_retrieve_recipes(self):
        # sample_recipe(user=self.user,
        #               ingredients=Ingredient.objects.create(user=self.user,
        #                                                     name='Kale'))
        sample_recipe(user=self.user)

        ing = Ingredient.objects.create(user=self.user, name='Kale')
        rec = sample_recipe(user=self.user)
        # this is how we assign data to many to many field
        rec.ingredients.add(ing)
        # serializer.data
        # OrderedDict([('id', 5),
        # ('title', 'Sample recipe'),
        # ('ingredients', [7]), ('tags', []),
        # ('time_miniutes', 10), ('price', '5.00'), ('link', '')]

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        # print(serializer.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            'other@test.com',
            'testpass'
        )
        sample_recipe(self.user)
        sample_recipe(user2, title="other")

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        recipe = sample_recipe(user=self.user)
        # adding data to many to many field
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        res = self.client.get(detail_url(recipe.id))

        # we dont need many=True as this is a single object
        serializer = RecipeDetailSerializer(recipe)
        # print(serializer.data)
        # {'id': 6,
        # 'title': 'Sample recipe',
        # 'ingredients': [OrderedDict([('id', 8),
        #                              ('name', 'sample ingredient')])],
        # 'tags': [OrderedDict([('id', 2), ('name', 'main course')])],
        # 'time_miniutes': 10, 'price': '5.00', 'link': ''}

        self.assertEqual(res.data, serializer.data)

    # test recipe creation with default params
    def test_create_basic_recipe(self):
        payload = {
            'title': 'choco cheese cake',
            'time_miniutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        # check if each of those payload keys are assigned
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    # test recipe creation with Tags
    def test_create_recipe_with_tags(self):
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Dessert")

        payload = {
            'title': 'choco cheese cake',
            'time_miniutes': 30,
            'price': 5.00,
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        # assert in is used to check if a value is in a list / queryset
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    # test recipe creation with ingredients
    def test_create_recipe_with_ingredients(self):
        ingredient1 = sample_ingredient(user=self.user, name="coco")
        ingredient2 = sample_ingredient(user=self.user, name="creme")
        payload = {
            'title': 'choco cheese cake',
            'time_miniutes': 30,
            'price': 5.00,
            'ingredients': [ingredient1.id, ingredient2.id]
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        # assert in is used to check if a value is in a list / queryset
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    # test partial update recipe (PATCH)
    def test_partial_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        # now lets replace this tag with a new tag
        new_tag = sample_tag(self.user, name="curry")
        payload = {
            'title': 'indian curry',
            'tags': [new_tag.id]
        }
        self.client.patch(detail_url(recipe.id), payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    # test full update of recipe (PUT)
    def test_full_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'new title',
            'time_miniutes': 7,
            'price': 12.00
        }
        self.client.put(detail_url(recipe.id), payload)

        recipe.refresh_from_db()

        # check if each of those payload keys are assigned
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        # check if tags is empty
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)

    # for delete
    # self.client.delete(detail_url(recipe.id))


class RecipeImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    # destructor. Clean up after test is completed
    def tearDown(self):
        self.recipe.image.delete()

    # test image upload
    def test_upload_image_to_recipe(self):
        # Create a image file object
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            # 10x10 black image
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)

            # ntf is the file objet which has to to passed to Image field
            res = self.client.post(image_upload_url(self.recipe.id),
                                   {'image': ntf},
                                   format='multipart')

        # at this point ntf is not available in file system
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    # test image upload bad request
    def test_upload_image_bad_request(self):
        res = self.client.post(image_upload_url(self.recipe.id),
                               {'image': 'notimage'},
                               format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
