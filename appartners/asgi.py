"""
ASGI config for appartners project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appartners.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import after Django setup to avoid AppRegistryNotReady exception
from chat.consumers import ChatConsumer, UserConsumer
from appartners.jwt_auth_middleware import JWTAuthMiddleware

# Define WebSocket URL patterns
websocket_urlpatterns = [
    path('ws/chat/<int:room_id>/', ChatConsumer.as_asgi()),
    path('ws/user/<int:user_id>/', UserConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
