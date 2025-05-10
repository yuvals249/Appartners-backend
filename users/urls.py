from django.urls import path

from .views.user_views import UserDetailsList, UserPreferencesPayloadView
from .views.user_preferences_views import UserPreferencesView
from .views.auth_views import LoginView, ValidateUniqueView, RegisterView
from .views.city_views import CityPayloadView
from .views.questionnaire_views import QuestionnaireView, UserResponseView
from .views.user_update_views import UpdatePasswordView, UpdateUserDetailsView
from .views.device_token_views import DeviceTokenView


users_urlpatterns = [
    path('user-details/', UserDetailsList.as_view(), name='user-details'),
    path('preferences/payload/', UserPreferencesPayloadView.as_view(), name='user-preferences-payload'),
    path('preferences/', UserPreferencesView.as_view(), name='user-preferences'),
    path('update-password/', UpdatePasswordView.as_view(), name='update-password'),
    path('update-details/', UpdateUserDetailsView.as_view(), name='update-details'),
    path('device-token/', DeviceTokenView.as_view(), name='device-token'),
]

auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('validate-unique/', ValidateUniqueView.as_view(), name='validate-unique'),
    path('payload/', CityPayloadView.as_view(), name='city-payload'),
]

questionnaire_urlpatterns = [
    path('', QuestionnaireView.as_view(), name='questionnaire'),
    path('responses/', UserResponseView.as_view(), name='questionnaire-responses'),
]
