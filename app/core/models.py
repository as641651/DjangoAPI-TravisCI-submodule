from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                            PermissionsMixin
# recommended way to retrieve settings from settings.py
from django.conf import settings
# to create unique id for files
import uuid
import os


def recipe_image_file_path(instance, filename):
    """ generate filepath for new image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/recipe/', filename)


# Creating CUSTOM USER MODEL
class UserManager(BaseUserManager):
    """Default User model requires mandatory username field
    But we dont want it that way. So we create custom User model"""

    def create_user(self, email, password=None, **kwargs):
        """Creates and saves a new user and returns the user model"""

        # this creates a model with mandatory email field
        if not email:
            raise ValueError('Usersmust have email')
        # normalize_email is under BaseUSerManager.
        # It makes domain part of email to lower case
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of password"""

    # all the fields we need
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # map the username field
    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """ Tag to be set for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Ingredient to be used in a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Ingredient to be used in a recipe"""
    # one to many: one user for many recipies
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_miniutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)

    # For optional fields, prefer blank over null.
    # If we set null, then in the code we have to check
    # for both null and empty str
    link = models.CharField(max_length=255, blank=True)

    # many to many field is just a repeatable foreign key field
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')

    # Image field
    # calls a function to find the file path
    # Input to this field is a file object
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title
