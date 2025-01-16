from rest_framework import serializers

from users.models.login_info import LoginInfo


class LoginInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginInfo
        fields = ('email', 'password')
