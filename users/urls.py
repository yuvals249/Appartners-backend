from django.urls import path

from .views import (
    UserDetailsList,
    UserPreferencesList,
    LoginView
)


users_urlpatterns = [
    path('userDetails/', UserDetailsList.as_view(), name='user-details'),
    path('userPreferences/', UserPreferencesList.as_view(), name='user-preferences'),
    path('questionnaire/payload/', UserPreferencesList.as_view(), name='user-preferences'),
]

auth_urlpatterns = [
    # path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]

