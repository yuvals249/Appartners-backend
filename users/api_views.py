from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from users.serializers import LoginInfoSerializer, UserDetailsSerializer, UserPreferencesSerializer
from users.models import LoginInfo, UserDetails, UserPreferences


class LoginInfoList(ListAPIView):
    queryset = LoginInfo.objects.all()
    serializer_class = LoginInfoSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('email',)

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