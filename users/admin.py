from django.contrib import admin
from .models.login_info import LoginInfo
from .models.questionnaire import Questionnaire
from .models.user_details import UserDetails
from .models.user_preferences import UserPreferences
from .models.user_preferences_features import UserPreferencesFeatures

from django.contrib.auth.hashers import make_password

# Admin for LoginInfo
@admin.register(LoginInfo)
class LoginInfoAdmin(admin.ModelAdmin):
    # Exclude password from admin display

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


@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    # Search fields in the admin table
    search_fields = ('first_name', 'last_name', 'phone_number')

    list_display = ('full_name',)

    @admin.display(description='Full Name')
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    # Search fields in the admin table
    search_fields = ('city', 'min_price', 'max_price')

    # Display email and created_at in the admin list view
    list_display = ('city', 'min_price', 'max_price', 'move_in_date', 'number_of_roommates')
