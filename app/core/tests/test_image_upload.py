from unittest.mock import patch
from django.test import TestCase
from core import models


class ImageManagerTest(TestCase):

    # change image name with uuid for unique identification
    @patch('uuid.uuid4')
    def test_image_filename_uuid(self, mock_uuid):
        # mock the generated uuid with test uuid
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        original_filename = 'myimage.jpg'
        file_path = models.recipe_image_file_path(None, original_filename)
        expected_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, expected_path)
