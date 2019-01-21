from rest_framework import serializers
from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)

    # create is not implemented here because
    # the user which is needed to create Tag is not defined here


class IngredientSerializer(serializers.ModelSerializer):
    """ Serializer for ingredient object"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


# This serializer points nested objects to its primary keys
class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for Recipe object """

    # specify the pointing fields for nested objects
    # without these fields, CREATE fails. GET however works
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        # ingredients and tag by default refer to its primary keys
        fields = ('id', 'title', 'ingredients', 'tags',
                  'time_miniutes', 'price', 'link')
        read_only_fields = ('id',)


# This serializer points its nested object to its own serializer
class RecipeDetailSerializer(RecipeSerializer):
    """ Serialize Recipe object """
    # Nesting serializers inside serializers
    # override nested objects
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


# Recipe serializer with image field
class RecipeImageSerializer(serializers.ModelSerializer):
    """serializer for uploading images to recipes"""
    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
