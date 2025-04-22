import json
import logging

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
