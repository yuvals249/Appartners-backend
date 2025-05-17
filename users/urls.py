from django.urls import path

from .views.user_views import UserDetailsList, UserPreferencesPayloadView, CurrentUserView
from .views.user_preferences_views import UserPreferencesView
from .views.auth_views import LoginView, ValidateUniqueView, RegisterView
from .views.city_views import CityPayloadView
from .views.questionnaire_views import QuestionnaireView, UserResponseView
from .views.user_update_views import UpdatePasswordView, UpdateUserDetailsView
from .views.device_token_views import DeviceTokenView
from .views.user_like_views import UserLikeView
from .views.token_refresh_views import TokenRefreshView
from .views.logout_views import LogoutView


users_urlpatterns = [
    path('user-details/', UserDetailsList.as_view(), name='user-details'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('preferences/payload/', UserPreferencesPayloadView.as_view(), name='user-preferences-payload'),
    path('preferences/', UserPreferencesView.as_view(), name='user-preferences'),
    path('update-password/', UpdatePasswordView.as_view(), name='update-password'),
    path('update-details/', UpdateUserDetailsView.as_view(), name='update-details'),
    path('device-token/', DeviceTokenView.as_view(), name='device-token'),
    path('like/', UserLikeView.as_view(), name='user-like'),
]

auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('validate-unique/', ValidateUniqueView.as_view(), name='validate-unique'),
    path('payload/', CityPayloadView.as_view(), name='city-payload'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

questionnaire_urlpatterns = [
    path('', QuestionnaireView.as_view(), name='questionnaire'),
    path('responses/', UserResponseView.as_view(), name='questionnaire-responses'),
]
