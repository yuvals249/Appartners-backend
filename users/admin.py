from django.contrib import admin
from .models import LoginInfo, UserDetails, UserPreferences
from django.contrib.auth.hashers import make_password

# Register your models here.
from . import models


# Admin for LoginInfo
class LoginInfoAdmin(admin.ModelAdmin):
    # Exclude password from admin display
    readonly_fields = ('email', 'password',)

    # Search fields in the admin table
    search_fields = ('email',)

    # Display email and created_at in the admin list view
    list_display = ('email',)

    # Override save_model to hash password
    def save_model(self, request, obj, form, change):
        # Only hash the password if it’s a new entry or if the password was changed
        if not obj.pk or 'password' in form.changed_data:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


class UserDetailsAdmin(admin.ModelAdmin):
    # Search fields in the admin table
    search_fields = ('first_name', 'last_name', 'phone_number')

    list_display = ('full_name',)

    @admin.display(description='Full Name')
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class UserPreferencesAdmin(admin.ModelAdmin):
    # Search fields in the admin table
    search_fields = ('area', 'min_price', 'max_price')

    # Display email and created_at in the admin list view
    list_display = ('area', 'min_price', 'max_price', 'move_in_date', 'number_of_roommates')


# Register the models and admin classes
admin.site.register(LoginInfo, LoginInfoAdmin)
admin.site.register(UserDetails, UserDetailsAdmin)
admin.site.register(UserPreferences, UserPreferencesAdmin)
