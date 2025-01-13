from django.contrib import admin
from .models import Apartment, ApartmentPhoto, Feature, ApartmentFeature


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    """
    Admin view for Apartment model.
    """
    list_display = (
        'id', 'city', 'street', 'type',
        'house_number', 'floor',
        'number_of_rooms', 'number_of_available_rooms',
        'total_price', 'available_entry_date'
    )
    list_filter = ('city', 'type', 'available_entry_date')
    search_fields = ('city', 'street', 'type')
    ordering = ('-available_entry_date',)


@admin.register(ApartmentPhoto)
class ApartmentPhotoAdmin(admin.ModelAdmin):
    """
    Admin view for ApartmentPhoto model.
    """
    list_display = ('id', 'apartment', 'photo')
    list_filter = ('apartment',)
    search_fields = ('apartment__city', 'photo')


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    """
    Admin view for Feature model.
    """
    list_display = ('name', 'description', 'active')
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
    search_fields = ('apartment__city', 'feature__name')
