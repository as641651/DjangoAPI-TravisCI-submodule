from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer


# view for API creating new user.
class CreateUserView(generics.CreateAPIView):
    """Create a new user"""
    serializer_class = UserSerializer


# view for API validating user credentials and providing token
class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    # class that will render this page
    # works without this but does not create nice view in the browser
    # as it did when extended from generic views
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# view for API retrieving and updating user info
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # retrieve and return authenticated user
    # this method is also required for update (patch)
    def get_object(self):
        # authentication class assigns user to request
        return self.request.user
