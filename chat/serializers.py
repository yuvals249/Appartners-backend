from rest_framework import serializers
from .models import ChatRoom, Message
from users.serializers import UserBasicSerializer  # שינינו מ-UserSerializer ל-UserBasicSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'firebase_id', 'is_read']

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserBasicSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'created_at', 'last_message_at', 'last_message']
    
    def get_last_message(self, obj):
        last_message = obj.messages.first()
        if last_message:
            return MessageSerializer(last_message).data
        return None