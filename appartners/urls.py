from django.urls import path, include, re_path
from django.contrib import admin
from users.urls import users_urlpatterns, auth_urlpatterns, questionnaire_urlpatterns
from apartments.urls import urlpatterns as apartments_urlpatterns

# Before Chat visualization at the backend
# from chat.urls import router

# Chat visualization at the backend
from chat.urls import urlpatterns as chat_urlpatterns

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    path('api/v1/users/', include(users_urlpatterns)),
    path('api/v1/apartments/', include(apartments_urlpatterns)),
    path('api/v1/authenticate/', include(auth_urlpatterns)),
    path('api/v1/questionnaire/', include(questionnaire_urlpatterns)),
    
    # Before Chat visualization at the backend
    # path('api/v1/chat/', include(router.urls)),
    
    # Chat visualization at the backend
    path('api/v1/chat/', include(chat_urlpatterns)),
]