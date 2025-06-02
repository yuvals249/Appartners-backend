from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet

# Chat visualization at the backend
from .views import chat_view

"""
URL Configuration for the Chat Application

This module defines the URL patterns for the chat functionality, including both
API endpoints and web interface views. It uses DRF's DefaultRouter for RESTful
API endpoints and adds a custom path for the web chat interface.
"""

router = DefaultRouter()
# Registers the ChatViewSet with the router, creating the following endpoints:
# - GET /api/v1/chat/rooms/ - List all chat rooms
# - POST /api/v1/chat/rooms/ - Create a new chat room
# - GET /api/v1/chat/rooms/{id}/ - Get specific chat room
# - POST /api/v1/chat/rooms/send_message_to_user/ - Send message to user
# - GET /api/v1/chat/rooms/{id}/messages/ - Get messages from room
router.register('rooms', ChatViewSet, basename='chat-room')

urlpatterns = [
    # Chat visualization at the backend
    path('web/', chat_view, name='chat-web'),

    # Explicit POST endpoint for sending messages
    path('rooms/send_message_to_user/', ChatViewSet.as_view({'post': 'send_message_to_user'}), name='send-message'),

    # Include all router-generated URLs
    # This adds all the RESTful endpoints created by the router
    path('', include(router.urls)),

]