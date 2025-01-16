from django.contrib import admin
from .models.user_details import UserDetails
from .models.user_preferences import UserPreferences


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
