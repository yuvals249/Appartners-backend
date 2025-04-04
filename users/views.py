"""
This file is maintained for backward compatibility.
All views have been moved to the views/ directory for better organization.
"""

from users.views.auth_views import ValidateUniqueView, LoginView, RegisterView
from users.views.user_views import UserDetailsList, UserPreferencesView
from users.views.city_views import CityPayloadView
from users.views.questionnaire_views import QuestionnaireView, UserResponseView

__all__ = [
    'ValidateUniqueView',
    'LoginView',
    'RegisterView',
    'UserDetailsList',
    'UserPreferencesView',
    'CityPayloadView',
    'QuestionnaireView',
    'UserResponseView',
]
