from django.urls import path

from .views import (
    UserDetailsList,
    LoginView,
    UserPreferencesView,
    ValidateUniqueView,
    CityPayloadView,
)


users_urlpatterns = [
    path('userDetails/', UserDetailsList.as_view(), name='user-details'),
    # path('userPreferences/', UserPreferencesView.as_view(), name='user-preferences'),
    # path('questionnaire/payload/', UserPreferencesView.as_view(), name='user-preferences'),
    path('preferences/<str:user_preferences_id>/', UserPreferencesView.as_view(), name='user-preferences-get'),
]

auth_urlpatterns = [
    # path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('validate-unique/', ValidateUniqueView.as_view(), name='validate-unique'),
    path('payload/', CityPayloadView.as_view(), name='city-payload'),
]
