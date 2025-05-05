import logging
import jwt
from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

logger = logging.getLogger('appartners')

@database_sync_to_async
def get_user(user_id):
    """
    Get user by ID from the database.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        User: The user object if found
        AnonymousUser: If the user is not found
    """
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return AnonymousUser()
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware for JWT authentication in WebSocket connections.

    This middleware extracts the JWT token from the WebSocket connection's
    query parameters, decodes it, and sets the authenticated user in the scope.

    Example URL with token:
        ws://example.com/ws/chat/1/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """

    async def __call__(self, scope, receive, send):
        """
        Process the WebSocket connection.

        Args:
            scope: The connection scope
            receive: The receive channel
            send: The send channel
        """
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            try:
                # Decode the JWT token
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')

                if user_id:
                    # Get the user from the database
                    user = await get_user(user_id)
                    scope['user'] = user
                    logger.info(f"WebSocket authenticated for user ID: {user_id}")
                else:
                    logger.warning("Token payload missing user_id")
                    scope['user'] = AnonymousUser()
            except jwt.ExpiredSignatureError:
                logger.warning("Token has expired")
                scope['user'] = AnonymousUser()
            except jwt.InvalidTokenError:
                logger.warning("Invalid token")
                scope['user'] = AnonymousUser()
            except Exception as e:
                logger.error(f"Error authenticating WebSocket: {str(e)}")
                scope['user'] = AnonymousUser()
        else:
            logger.warning("No token provided in WebSocket connection")
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
