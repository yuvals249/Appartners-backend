"""
Firebase Cloud Messaging service for sending push notifications.
"""
import logging
from firebase_admin import messaging
from users.models import DeviceToken

logger = logging.getLogger(__name__)


class FirebaseService:
    """
    Service for sending push notifications via Firebase Cloud Messaging.
    """
    @staticmethod
    def send_notification(user_id, title, body, data=None):
        """
        Send a push notification to a specific user.
        
        Args:
            user_id: ID of the user to send the notification to
            title: Notification title
            body: Notification body text
            data: Optional dictionary of additional data to send
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        try:
            # Get all active device tokens for the user
            device_tokens = DeviceToken.objects.filter(
                user_id=user_id, 
                is_active=True
            ).values_list('token', flat=True)
            
            if not device_tokens:
                logger.warning(f"No active device tokens found for user_id {user_id}")
                return False
                
            # Prepare the message
            message = messaging.MulticastMessage(
                tokens=list(device_tokens),
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='notification_icon',
                        color='#4CAF50',
                        sound='default'
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                            content_available=True
                        )
                    )
                ),
            )
            
            # Send the message
            response = messaging.send_multicast(message)
            
            # Log the response
            logger.info(f"Sent notification to {len(device_tokens)} devices. Success: {response.success_count}, Failure: {response.failure_count}")
            
            # Handle failures if needed
            if response.failure_count > 0:
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        logger.error(f"Failed to send notification to token {device_tokens[idx]}: {resp.exception}")
                        
                        # If token is invalid, mark it as inactive
                        if resp.exception and 'invalid-registration-token' in str(resp.exception).lower():
                            DeviceToken.objects.filter(token=device_tokens[idx]).update(is_active=False)
            
            return response.success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False
            
    @staticmethod
    def send_apartment_like_notification(apartment_owner_id, liker_name, apartment_title):
        """
        Send a notification to the apartment owner when someone likes their apartment.
        
        Args:
            apartment_owner_id: ID of the apartment owner
            liker_name: Name of the user who liked the apartment
            apartment_title: Title of the apartment
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        title = "New Like on Your Apartment!"
        body = f"{liker_name} liked your apartment: {apartment_title}"
        
        data = {
            "notification_type": "apartment_like",
            "apartment_title": apartment_title,
            "liker_name": liker_name
        }
        
        return FirebaseService.send_notification(apartment_owner_id, title, body, data)
