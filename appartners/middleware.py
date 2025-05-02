import json
import logging
from django.utils import timezone
from django.contrib.auth.models import User
from users.models.user_presence import UserPresence

logger = logging.getLogger(__name__)

class RequestResponseLoggingMiddleware:
    """
    Middleware to log request and response details, especially for 400 Bad Request responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Log 400 Bad Request responses
        if response.status_code == 400:
            # Log the request path and method
            logger.error(f"400 Bad Request: {request.method} {request.path}")

            # Try to log request body
            try:
                if request.body:
                    body = request.body.decode('utf-8')
                    try:
                        # Try to parse as JSON for better formatting
                        body_json = json.loads(body)
                        logger.error(f"Request Body: {json.dumps(body_json, indent=2)}")
                    except json.JSONDecodeError:
                        # If not JSON, log as is
                        logger.error(f"Request Body: {body}")
            except Exception as e:
                logger.error(f"Error logging request body: {str(e)}")

            # Try to log response body
            try:
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')
                    try:
                        # Try to parse as JSON for better formatting
                        content_json = json.loads(content)
                        logger.error(f"Response Body: {json.dumps(content_json, indent=2)}")
                    except json.JSONDecodeError:
                        # If not JSON, log as is
                        logger.error(f"Response Body: {content}")
            except Exception as e:
                logger.error(f"Error logging response body: {str(e)}")

        return response


class UserPresenceMiddleware:
    """
    Middleware to update user's last_seen_at timestamp.

    This middleware checks if the request has an authenticated user and updates
    their last_seen_at timestamp in the UserPresence model.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Update user's last_seen_at if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                # Get or create UserPresence for the user
                presence, created = UserPresence.objects.get_or_create(user=request.user)
                presence.update_presence()
            except Exception as e:
                # Check if the error is due to the table not existing
                if 'relation "users_userpresence" does not exist' in str(e):
                    logger.error(f"Error updating user presence: {str(e)}")
                    # Skip updating presence if the table doesn't exist
                    pass
                else:
                    # Log other errors
                    logger.error(f"Error updating user presence: {str(e)}")

        return response
