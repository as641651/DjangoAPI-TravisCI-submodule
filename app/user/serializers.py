from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


# This serializer is for for an API that will add data to a model
class UserSerializer(serializers.ModelSerializer):
    """serializer for user object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')

        # the password should be write only.
        # it should not be serialized when get is called
        # we specify extra kwargs for each field
        # list of accepted args for can be found under core argument section of
        # https://www.django-rest-framework.org/api-guide/fields/
        # for password field, args under serializer.CharField are also valid
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # create is called when we use the CreateAPI view
    # which takes a POST request to create a user
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


# Serializer can also be used without a model
# Since this is not a model, we inherit from serializers.Serializer
# This is for an API that will get some data from user, validate it
# and return some value
class AuthTokenSerializer(serializers.Serializer):
    """serializer for user authentication object"""
    # create fields to get data for authentication
    email = serializers.CharField()
    password = serializers.CharField(
                style={'input_type': 'password'},
                trim_whitespace=False
                )

    # override validate method and raise exception if invalid
    def validate(self, attrs):
        # attrs contains all the serializer fields defined above
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
        if not user:
            # we use gettext to enable language tranlation for this text
            msg = _("Unable to authenticate with credentials provided")
            # pass correct code will raise the relavant http status code
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
