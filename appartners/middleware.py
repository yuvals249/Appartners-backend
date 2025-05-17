import json
import logging
from django.utils import timezone
from django.contrib.auth.models import User
from users.models.user_presence import UserPresence

logger = logging.getLogger(__name__)

class RequestResponseLoggingMiddleware:
    """
    Middleware to log request and response details for all requests.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log all requests
        self._log_request(request)
        
        # Process the request
        response = self.get_response(request)

        # Log error responses (400, 500, etc.)
        if response.status_code >= 400:
            self._log_response(response)

        return response
    
    def _log_request(self, request):
        """
        Log request details including URL, method, and body.
        """
        # Log the request path and method
        logger.info(f"REQUEST: {request.method} {request.path}")
        
        # Skip logging for certain paths (like static files, admin, etc.)
        if any(path in request.path for path in ['/static/', '/media/', '/admin/jsi18n/']):
            return
            
        # Log query parameters if present
        if request.GET:
            logger.info(f"Query Params: {dict(request.GET)}")
        
        # Log POST/PUT data if it's form data
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'POST') and request.POST:
            logger.info(f"Form Data: {dict(request.POST)}")
            
        # Log FILES if present
        if hasattr(request, 'FILES') and request.FILES:
            file_info = {k: f"{v.name} ({v.size} bytes)" for k, v in request.FILES.items()}
            logger.info(f"Files: {file_info}")
        
        # Try to log request body
        try:
            if request.body:
                body = request.body.decode('utf-8')
                try:
                    # Try to parse as JSON for better formatting
                    body_json = json.loads(body)
                    logger.info(f"Request Body: {json.dumps(body_json, indent=2)}")
                except json.JSONDecodeError:
                    # If not JSON, log as is (truncate if too long)
                    if len(body) > 1000:
                        logger.info(f"Request Body (truncated): {body[:1000]}...")
                    else:
                        logger.info(f"Request Body: {body}")
        except Exception as e:
            logger.error(f"Error logging request body: {str(e)}")
    
    def _log_response(self, response):
        """
        Log response details including status code and body for error responses.
        """
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
