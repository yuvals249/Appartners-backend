from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet

# Chat visualization at the backend
from .views import chat_view

router = DefaultRouter()
router.register('rooms', ChatViewSet, basename='chat-room')

urlpatterns = [
    # Chat visualization at the backend
    path('web/', chat_view, name='chat-web'),

    path('', include(router.urls)),

]