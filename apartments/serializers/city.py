from rest_framework import serializers

from apartments.models import City, Apartment


class CitySerializer(serializers.ModelSerializer):
    areas = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = ['id', 'name', 'hebrew_name', 'areas']
    
    def get_areas(self, obj):
        """
        Get all distinct areas for this city from apartments
        """
        areas = Apartment.objects.filter(
            city=obj, 
            area__isnull=False
        ).exclude(
            area=""
        ).values_list('area', flat=True).distinct().order_by('area')
        
        return list(areas)