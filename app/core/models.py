from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                            PermissionsMixin


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
