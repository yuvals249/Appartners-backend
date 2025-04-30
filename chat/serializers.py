from rest_framework import serializers
from .models import ChatRoom, Message
from users.serializers import UserBasicSerializer

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
        is_read: Message read status
    """
    sender = UserBasicSerializer(read_only=True)  # Only basic user info is needed for messages
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'firebase_id', 'is_read']


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
    """
    participants = UserBasicSerializer(many=True, read_only=True)  # List of participants with basic info
    last_message = serializers.SerializerMethodField()  # Custom field for last message
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'created_at', 'last_message_at', 'last_message']
    
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
        last_message = obj.messages.first()  # Gets first message (newest due to ordering)
        if last_message:
            return MessageSerializer(last_message).data
        return None