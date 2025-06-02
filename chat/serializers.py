from rest_framework import serializers
from .models import ChatRoom, Message
from users.serializers import UserBasicSerializer
from users.models.user_presence import UserPresence
from django.contrib.auth.models import User
from apartments.models import Apartment
from apartments.models.apartment_user_like import ApartmentUserLike
from apartments.serializers.apartment import ApartmentSerializer
import logging

logger = logging.getLogger(__name__)

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages.

    This serializer handles the conversion of Message model instances to JSON format
    and vice versa. It includes the sender's basic information using UserBasicSerializer.

    Fields:
        sender: Basic user information of the message sender (read-only)
        id: Unique identifier for the message
        content: The actual message text
        timestamp: When the message was sent
        firebase_id: Reference ID for Firebase synchronization
        read_at: Timestamp when the message was read (null if unread)
        is_sender: Boolean indicating if the current user is the sender of this message
        is_read: Boolean indicating if the message has been read by the recipient
    """
    sender = UserBasicSerializer(read_only=True)  # Only basic user info is needed for messages
    is_sender = serializers.SerializerMethodField()  # Custom field to indicate if current user is sender
    is_read = serializers.SerializerMethodField()  # Custom field to indicate if message is read

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'firebase_id', 'read_at', 'is_sender', 'is_read']

    def get_is_sender(self, obj):
        """
        Determines if the current user is the sender of this message.

        Args:
            obj (Message): The message instance being serialized

        Returns:
            bool: True if the current user is the sender, False otherwise
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
        return obj.sender.id == request.user.id

    def get_is_read(self, obj):
        """
        Determines if the message has been read by the recipient.

        Args:
            obj (Message): The message instance being serialized

        Returns:
            bool: True if the message has been read, False otherwise
        """
        return obj.read_at is not None


class ChatRoomSerializer(serializers.ModelSerializer):
    """
    Serializer for chat rooms.

    This serializer handles the conversion of ChatRoom model instances to JSON format.
    It includes the list of participants and the most recent message in the room.

    Fields:
        id: Unique identifier for the chat room
        participants: List of users in the chat room (read-only)
        created_at: When the room was created
        last_message_at: Timestamp of the most recent message
        last_message: Details of the most recent message (computed field)
        other_user_last_seen: When the other user in the chat was last seen (computed field)
        unread_count: Number of unread messages in this chat room for the current user (computed field)
        last_message_sender_id: ID of the user who sent the last message (computed field)
        last_message_read_at: Timestamp when the last message was read (computed field)
        was_last_message_sent_by_me: Boolean indicating if the current user sent the last message (computed field)
        connected_apartment: Apartment connecting users in the chat room (computed field)
    """
    participants = UserBasicSerializer(many=True, read_only=True)  # List of participants with basic info
    last_message = serializers.SerializerMethodField()  # Custom field for last message
    other_user_last_seen = serializers.SerializerMethodField()  # Custom field for other user's last seen timestamp
    unread_count = serializers.SerializerMethodField()  # Custom field for unread message count
    last_message_sender_id = serializers.SerializerMethodField()  # ID of the user who sent the last message
    last_message_read_at = serializers.SerializerMethodField()  # Timestamp when the last message was read
    was_last_message_sent_by_me = serializers.SerializerMethodField()  # Boolean indicating if current user sent the last message
    connected_apartment = serializers.SerializerMethodField()  # Custom field for apartment connecting users

    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'created_at', 'last_message_at', 'last_message', 'other_user_last_seen', 'unread_count', 
                 'last_message_sender_id', 'last_message_read_at', 'was_last_message_sent_by_me', 'connected_apartment']

    def get_last_message(self, obj):
        """
        Retrieves the most recent message in the chat room.

        This method is automatically called by DRF to populate the last_message field.
        It uses the messages reverse relation and the ordering defined in the Message model.

        Args:
            obj (ChatRoom): The chat room instance being serialized

        Returns:
            dict: Serialized data of the last message if it exists
            None: If the room has no messages
        """
        last_message = obj.messages.last()  # Gets last message (newest due to ascending timestamp ordering)
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_other_user_last_seen(self, obj):
        """
        Retrieves the last seen timestamp of the other user in the chat.

        This method is automatically called by DRF to populate the other_user_last_seen field.
        It identifies the other user in the chat (not the current user) and returns their
        last_seen_at timestamp from the UserPresence model.

        Args:
            obj (ChatRoom): The chat room instance being serialized

        Returns:
            str: ISO format timestamp of when the other user was last seen
            None: If the other user has no presence record or if the current user is not in the request
                  or if the UserPresence table doesn't exist
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return None

        # Find the other user in the chat (not the current user)
        other_user = None
        for participant in obj.participants.all():
            if participant.id != request.user.id:
                other_user = participant
                break

        if not other_user:
            return None

        # Get the other user's presence record
        try:
            presence = UserPresence.objects.get(user=other_user)
            return presence.last_seen_at.isoformat()
        except UserPresence.DoesNotExist:
            return None
        except Exception as e:
            # Handle case where UserPresence table doesn't exist
            if 'relation "users_userpresence" does not exist' in str(e):
                return None
            # Re-raise any other exceptions
            raise

    def get_unread_count(self, obj):
        """
        Counts the number of unread messages in this chat room for the current user.

        This method is automatically called by DRF to populate the unread_count field.
        It counts messages where the sender is not the current user and read_at is None.

        Args:
            obj (ChatRoom): The chat room instance being serialized

        Returns:
            int: Number of unread messages
            0: If there are no unread messages or if the current user is not in the request
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return 0

        # Count messages where the sender is not the current user and read_at is None
        return obj.messages.exclude(
            sender=request.user
        ).filter(
            read_at__isnull=True
        ).count()

    def get_last_message_sender_id(self, obj):
        """
        Retrieves the ID of the user who sent the last message in the chat room.

        Args:
            obj (ChatRoom): The chat room instance being serialized

        Returns:
            int: User ID of the sender of the last message
            None: If the room has no messages
        """
        last_message = obj.messages.last()
        if last_message:
            return last_message.sender.id
        return None

    def get_last_message_read_at(self, obj):
        """
        Retrieves the timestamp when the last message in the chat room was read.

        Args:
            obj (ChatRoom): The chat room instance being serialized

        Returns:
            str: ISO format timestamp of when the last message was read
            None: If the room has no messages or if the last message hasn't been read
        """
        last_message = obj.messages.last()
        if last_message and last_message.read_at:
            return last_message.read_at.isoformat()
        return None

    def get_was_last_message_sent_by_me(self, obj):
        """
        Determines if the current user sent the last message in the chat room.

        Args:
            obj (ChatRoom): The chat room instance being serialized

        Returns:
            bool: True if the current user sent the last message, False otherwise
            None: If the room has no messages or if the current user is not in the request
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return None

        last_message = obj.messages.order_by('-timestamp').first()
        if not last_message:
            return None

        return last_message.sender.id == request.user.id
        
    def get_connected_apartment(self, obj):
        """
        Find the apartment that connects the users in a chat room.
        Returns the first apartment that one user owns and the other user has liked.
        
        Args:
            obj (ChatRoom): The chat room instance being serialized
            
        Returns:
            dict: Serialized apartment data if a connection exists
            None: If no connecting apartment is found
        """
        try:
            request = self.context.get('request')
            if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
                return None
                
            # Need at least 2 participants to find a connection
            if obj.participants.count() < 2:
                return None
                
            # Get the current user and the other user in the chat
            current_user = request.user
            other_user = obj.participants.exclude(id=current_user.id).first()
            
            if not other_user:
                return None
                
            # Find apartments owned by current user that other user liked
            current_user_apartments = Apartment.objects.filter(user=current_user)
            for apartment in current_user_apartments:
                liked = ApartmentUserLike.objects.filter(apartment=apartment, user=other_user, like=True).exists()
                if liked:
                    return ApartmentSerializer(apartment, context={'request': request}).data
            
            # Find apartments owned by other user that current user liked
            other_user_apartments = Apartment.objects.filter(user=other_user)
            for apartment in other_user_apartments:
                liked = ApartmentUserLike.objects.filter(apartment=apartment, user=current_user, like=True).exists()
                if liked:
                    return ApartmentSerializer(apartment, context={'request': request}).data
            
            return None
        except Exception as e:
            logger.error(f"Error finding connected apartment: {str(e)}")
            return None