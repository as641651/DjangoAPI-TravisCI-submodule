from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from recipe import serializers


# viewset is used when a separate url is mapped to this view for each user
# /api/recepi/tags/ : mapped separately for each user
class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # This method should be overriden
    # if we dont want to modify query set based on current instance attributes
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # override this method for CreateModelMixin
    # create operation is done here (unlike in UserModelSerializer)
    # because serializer does not have user
    # we pass user to serializer and save it
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
