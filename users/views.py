from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.response import Response


from users.serializers.login_info import LoginInfoSerializer
from users.serializers.user_details import UserDetailsSerializer
from users.serializers.user_preferences import UserPreferencesSerializer

from users.models.login_info import LoginInfo
from users.models.user_details import UserDetails
from users.models.user_preferences import UserPreferences


class LoginInfoList(ListAPIView):
    def get(self, request, *args, **kwargs):
        queryset = LoginInfo.objects.all()
        serializer_class = LoginInfoSerializer(queryset, many=True)
        return Response(serializer_class.data)


class UserDetailsList(ListAPIView):
    queryset = UserDetails.objects.all()
    serializer_class = UserDetailsSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('id',)
    search_fields = ('first_name', 'last_name', 'phone_number',)


class UserPreferencesList(ListAPIView):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('id', 'area', 'max_price', 'move_in_date', 'number_of_roommates')
