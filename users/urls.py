from django.urls import path

from .views import (
    LoginInfoList,
    UserDetailsList,
    UserPreferencesList,
)


urlpatterns = [
    path('loginInfo/', LoginInfoList.as_view(), name='login-info'),
    path('userDetails/', UserDetailsList.as_view(), name='user-details'),
    path('userPreferences/', UserPreferencesList.as_view(), name='user-preferences'),
    path('questionnaire/payload/', UserPreferencesList.as_view(), name='user-preferences'),
    path('<str:apartment_id>/', ApartmentView.as_view(), name='apartment-get')

]

