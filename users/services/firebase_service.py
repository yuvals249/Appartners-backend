"""
Firebase Cloud Messaging service for sending push notifications.
"""
import os
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
            # Get the first active device token for the user
            device_tokens = DeviceToken.objects.filter(
                user_id=user_id, 
                is_active=True
            ).values_list('token', flat=True)
            logger.info(f"Device tokens for user_id {user_id}: {device_tokens}")
            
            if not device_tokens:
                logger.warning(f"No active device tokens found for user_id {user_id}")
                return False
            
            # Just use the first token
            token = device_tokens[0]
            
            try:
                # Prepare the message for a single token
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    token=token,
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
                    webpush=messaging.WebpushConfig(
                        notification=messaging.WebpushNotification(
                            icon='https://www.gstatic.com/mobilesdk/160503_mobilesdk/logo/2x/firebase_96dp.png',
                            badge='https://www.gstatic.com/mobilesdk/160503_mobilesdk/logo/2x/firebase_28dp.png',

                            actions=[
                                messaging.WebpushNotificationAction(
                                    action='view',
                                    title='View Details'
                                )
                            ],
                            vibrate=[100, 50, 100],  # Vibration pattern
                            require_interaction=True  # Makes notification stay until user interacts with it
                        ),
                    ),
                )
                
                # Send the message to the token
                response = messaging.send(message)
                logger.info(f"Successfully sent message to token {token[:16]}...: {response}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to send notification to token {token[:16]}...: {str(e)}")
                
                # If token is invalid, mark it as inactive
                if 'invalid-registration-token' in str(e).lower():
                    DeviceToken.objects.filter(token=token).update(is_active=False)
                return False
            
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
