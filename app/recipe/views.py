from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe import serializers


# viewset is used when a separate url is mapped to this view for each user
# /api/recepi/tags/ : mapped separately for each user
class BaseRecepiAttr(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # abstract attributes
    @property
    def serializer_class(self):
        raise NotImplementedError

    # ListModelMixin returns a list of objects when GET is called
    @property
    def queryset(self):
        raise NotImplementedError

    # This method should be overriden
    # if we dont want to modify query set based on current instance attributes
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # override this method for CreateModelMixin
    # create operation is done here (unlike in UserModelSerializer)
    # because serializer can not have user
    # we pass user to serializer and save it
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# viewset is used when a separate url is mapped to this view for each user
# /api/recepi/tags/ : mapped separately for each user
class TagViewSet(BaseRecepiAttr):
    """manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


# This class looks almost similar to previous class.
# Its better to write a common base class
# /api/recepi/ingredients/ : mapped separately for each user
class IngredientViewSet(BaseRecepiAttr):

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
