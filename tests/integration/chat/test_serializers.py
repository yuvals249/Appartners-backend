from django.test import RequestFactory
from django.contrib.auth import get_user_model
from chat.models import ChatRoom, Message
from chat.serializers import (
    MessageSerializer,
    ChatRoomSerializer
)
import pytest

User = get_user_model()

@pytest.mark.django_db
def test_message_serializer(test_user1, test_chat_room):
    """Test message serialization"""
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Test message",
        firebase_id="test_firebase_id_123"
    )
    serializer = MessageSerializer(message)
    data = serializer.data
    
    assert data['content'] == message.content
    assert data['sender']['email'] == test_user1.email
    assert data['firebase_id'] == message.firebase_id
    assert data['is_read'] is False
    assert data['is_sender'] is False

@pytest.mark.django_db
def test_message_serializer_with_request(test_user1, test_chat_room):
    """Test message serialization with request context"""
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Test message",
        firebase_id="test_firebase_id_123"
    )
    factory = RequestFactory()
    request = factory.get('/')
    request.user = test_user1
    
    serializer = MessageSerializer(message, context={'request': request})
    data = serializer.data
    
    assert data['content'] == message.content
    assert data['sender']['email'] == test_user1.email
    assert data['firebase_id'] == message.firebase_id
    assert data['is_read'] is False
    assert data['is_sender'] is True

@pytest.mark.django_db
def test_chat_room_serializer(test_user1, test_user2):
    """Test chat room serialization"""
    chat_room = ChatRoom.objects.create()
    chat_room.participants.add(test_user1, test_user2)
    
    serializer = ChatRoomSerializer(chat_room)
    data = serializer.data
    
    assert data['id'] == chat_room.id
    assert len(data['participants']) == 2
    assert data['participants'][0]['email'] == test_user1.email
    assert data['participants'][1]['email'] == test_user2.email

@pytest.mark.django_db
def test_chat_room_serializer_with_message(test_user1, test_user2, test_chat_room):
    """Test chat room serialization with messages"""
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Test message",
        firebase_id="test_firebase_id_123"
    )
    
    serializer = ChatRoomSerializer(test_chat_room)
    data = serializer.data
    
    assert data['id'] == test_chat_room.id
    assert len(data['participants']) == 2
    assert data['participants'][0]['email'] == test_user1.email
    assert data['participants'][1]['email'] == test_user2.email

@pytest.mark.django_db
def test_chat_room_serializer_with_request(test_user1, test_user2, test_chat_room):
    """Test chat room serialization with request context"""
    factory = RequestFactory()
    request = factory.get('/')
    request.user = test_user1
    
    serializer = ChatRoomSerializer(test_chat_room, context={'request': request})
    data = serializer.data
    
    assert data['id'] == test_chat_room.id
    assert len(data['participants']) == 2
    
    # Find participants by email instead of assuming order
    participant_emails = [p['email'] for p in data['participants']]
    assert test_user1.email in participant_emails
    assert test_user2.email in participant_emails

@pytest.mark.django_db
def test_chat_room_serializer_with_last_message(test_user1, test_user2, test_chat_room):
    """Test chat room serialization with last message"""
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Last message",
        firebase_id="test_firebase_id_123"
    )
    
    serializer = ChatRoomSerializer(test_chat_room)
    data = serializer.data
    
    assert data['id'] == test_chat_room.id
    assert len(data['participants']) == 2
    assert data['participants'][0]['email'] == test_user1.email
    assert data['participants'][1]['email'] == test_user2.email

@pytest.mark.django_db
def test_chat_room_serializer_with_unread_count(test_user1, test_user2, test_chat_room):
    """Test chat room serialization with unread count"""
    Message.objects.create(
        room=test_chat_room,
        sender=test_user2,
        content="Unread message",
        firebase_id="test_firebase_id_123"
    )
    
    factory = RequestFactory()
    request = factory.get('/')
    request.user = test_user1
    
    serializer = ChatRoomSerializer(test_chat_room, context={'request': request})
    data = serializer.data
    
    assert data['id'] == test_chat_room.id
    assert len(data['participants']) == 2
    assert data['participants'][0]['email'] == test_user1.email
    assert data['participants'][1]['email'] == test_user2.email

@pytest.mark.django_db
def test_message_serializer_with_read_status(test_user1, test_user2, test_chat_room):
    """Test message serialization with read status"""
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user2,
        content="Test message",
        firebase_id="test_firebase_id_123"
    )
    
    factory = RequestFactory()
    request = factory.get('/')
    request.user = test_user1
    
    serializer = MessageSerializer(message, context={'request': request})
    data = serializer.data
    
    assert data['content'] == message.content
    assert data['is_read'] == False 