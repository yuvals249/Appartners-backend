from django.contrib import admin
from apartments.models import Apartment, ApartmentPhoto, Feature, ApartmentFeature, City


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    """
    Admin view for Apartment model.
    """
    list_display = (
        'id', 'created_at', 'updated_at', 'street', 'type',
        'house_number', 'floor',
        'number_of_rooms', 'number_of_available_rooms',
        'total_price', 'available_entry_date'
    )
    list_filter = ('city', 'type', 'available_entry_date')
    search_fields = ('city__name', 'street', 'type')
    ordering = ('-created_at',)


@admin.register(ApartmentPhoto)
class ApartmentPhotoAdmin(admin.ModelAdmin):
    """
    Admin view for ApartmentPhoto model.
    """
    list_display = ('id', 'apartment', 'photo')
    list_filter = ('apartment',)
    search_fields = ('apartment__city__name', 'photo')


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    """
    Admin view for Feature model.
    """
    list_display = ('id', 'name', 'description', 'active')
    list_filter = ('active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(ApartmentFeature)
class ApartmentFeatureAdmin(admin.ModelAdmin):
    """
    Admin view for ApartmentFeature model.
    """
    list_display = ('id', 'apartment', 'feature')
    list_filter = ('apartment', 'feature')
    search_fields = ('apartment__city__name', 'feature__name')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """
    Admin view for City model.
    """
    list_display = ('id', 'name', 'hebrew_name')
    list_filter = ('name', 'hebrew_name')
    search_fields = ('name', 'hebrew_name')
