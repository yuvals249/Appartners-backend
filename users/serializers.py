from rest_framework import serializers

from users.models import LoginInfo, UserDetails, UserPreferences


class LoginInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginInfo
        fields = ('email', 'password')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ('first_name', 'last_name', 'gender', 'occupation', 'birth_date', 'address', 'phone_number')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['full_name'] = f'{instance.first_name} {instance.last_name}'
        return data


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ('area', 'min_price', 'max_price', 'move_in_date', 'number_of_roommates')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data
