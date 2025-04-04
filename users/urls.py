from django.urls import path

from .views import (
    UserDetailsList,
    LoginView,
    UserPreferencesView,
    ValidateUniqueView,
    CityPayloadView,
    RegisterView,
    QuestionnaireView,
    UserResponseView,
)


users_urlpatterns = [
    path('userDetails/', UserDetailsList.as_view(), name='user-details'),
    path('preferences/<str:user_preferences_id>/', UserPreferencesView.as_view(), name='user-preferences-get'),
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
