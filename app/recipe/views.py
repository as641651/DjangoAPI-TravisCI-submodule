from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe import serializers

# for image upload api view
from rest_framework.decorators import action
from rest_framework.response import Response


# viewset is used when dealing with multiple instances of a model.
# viewset is used when we intend to query or filter model objects
# /api/recepi/tags/ : mapped separately for each user
class BaseRecepiAttr(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
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
        assigned_only = bool(self.request.query_params.get('assigned_only'))
        queryset = self.queryset
        if assigned_only:
            # Django also allows access of reverse relation in foreign keys
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user).order_by('-name')

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


# Extend from 'ModelViewSet' has all request mixins
# API CALL (recipe-list) : /api/recipe/recipes
# API CALL (recipe-detail) : /api/recipe/recipes/<pk>/
class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()

    # django allows to change serializers depending on action
    # we can have differernt serializer for list and detail views
    # for this, we have to override this function
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    # helper function
    # _ prefix is used to indicate private function
    def _params_to_int(self, qs):
        """convert a list of string IDs to ints"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        # filtering based on params in payload
        # returns none if params are not available
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_int(tags)
            # djangos filter for attrs
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_int(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # write custom code when GET without id is called
    def list(self, request):
        # print("GET without id")
        return super().list(request)

    # write custom code when GET with ID is called
    def retrieve(self, request, pk):
        # print("GET with id")
        return super().retrieve(request, pk)

    # writing custom function on call to specific api with specific request
    # POST request to url to this appened with upload-image with pk arg(detail)
    # This function becomes a custom action = upload_image
    # API CALL (recipe-upload-image) : /api/recipe/recipes/<pk>/upload-image
    @action(methods=['POST', 'DELETE'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        # we have to encode our own Response
        # ie, we have to manually serialize our objects
        recipe = self.get_object()
        if(request.method == 'POST'):
            # modify get_serializer_class to consider this action
            serializer = self.get_serializer(recipe, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        elif(request.method == 'DELETE'):
            if recipe.image:
                recipe.image.delete()
                serializer = self.get_serializer(recipe)
                return Response(serializer.data, status=status.HTTP_200_OK)
