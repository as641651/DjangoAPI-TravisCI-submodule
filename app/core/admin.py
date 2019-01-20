from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
# this hook is needed to make django projects translatable,
# Wrap the texts with this if you want django to automatically translate
from django.utils.translation import gettext as _


# This class is used just for the admin interface.
# Nothing changes except the way admin page looks
class UserAdmin(BaseUserAdmin):
    ordering = ['id']

    # fields to be included in list users page
    list_display = ['email', 'name']

    # fields to be included on change user page (edit page)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
         ),
        (_('Important dates'), {'fields': ('last_login',)})
    )

    # fields to be included in add user page
    # therefore we can create a new user with email and password
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


# If we use the default admin class, we dont have to pass the second parameter
# Here we modified the default adin class
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
admin.site.register(models.Recipe)
