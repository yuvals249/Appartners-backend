from django.test import RequestFactory
from django.contrib.auth.models import User
from chat.models import ChatRoom, Message
from chat.serializers import (
    MessageSerializer,
    ChatRoomSerializer
)
from users.models import UserDetails
import pytest

@pytest.fixture
def test_user1(db):
    """Fixture ליצירת משתמש ראשון לבדיקות"""
    user = User.objects.create_user(
        username="user1",
        email="user1@example.com",
        password="testpass123"
    )
    UserDetails.objects.create(
        user=user,
        first_name="User",
        last_name="One",
        birth_date="1990-01-01",
        gender="M",
        phone_number="0501234567",
        occupation="Student",
        preferred_city="Tel Aviv"
    )
    return user

@pytest.fixture
def test_user2(db):
    """Fixture ליצירת משתמש שני לבדיקות"""
    user = User.objects.create_user(
        username="user2",
        email="user2@example.com",
        password="testpass123"
    )
    UserDetails.objects.create(
        user=user,
        first_name="User",
        last_name="Two",
        birth_date="1990-01-01",
        gender="F",
        phone_number="0507654321",
        occupation="Student",
        preferred_city="Tel Aviv"
    )
    return user

@pytest.fixture
def test_chat_room(db, test_user1, test_user2):
    """Fixture ליצירת חדר צ'אט לבדיקות"""
    chat_room = ChatRoom.objects.create(name="Test Chat Room")
    chat_room.participants.add(test_user1, test_user2)
    return chat_room

@pytest.fixture
def test_message(db, test_chat_room, test_user1):
    """Fixture ליצירת הודעה לבדיקות"""
    return Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Test message",
        firebase_id="test_firebase_id"
    )

def test_message_serializer(test_message, test_user1):
    """בדיקת סריאלייזר הודעה"""
    serializer = MessageSerializer(test_message)
    data = serializer.data

    assert data['content'] == "Test message"
    assert data['sender']['email'] == test_user1.email
    assert data['sender']['first_name'] == "User"
    assert data['sender']['last_name'] == "One"
    assert data['firebase_id'] == "test_firebase_id"
    assert data['is_read'] is False

def test_message_serializer_with_request(test_message, test_user1, rf):
    """בדיקת סריאלייזר הודעה עם קונטקסט של request"""
    request = rf.get('/')
    request.user = test_user1
    serializer = MessageSerializer(test_message, context={'request': request})
    data = serializer.data

    assert data['is_sender'] is True

def test_chat_room_serializer(test_chat_room, test_user1, test_user2):
    """בדיקת סריאלייזר חדר צ'אט"""
    serializer = ChatRoomSerializer(test_chat_room)
    data = serializer.data

    assert len(data['participants']) == 2
    assert any(p['email'] == test_user1.email for p in data['participants'])
    assert any(p['email'] == test_user2.email for p in data['participants'])
    assert data['unread_count'] == 0

def test_chat_room_serializer_with_message(test_chat_room, test_user1, test_user2):
    """בדיקת סריאלייזר חדר צ'אט עם הודעה"""
    # יצירת הודעה
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Test message",
        firebase_id="test_firebase_id"
    )

    serializer = ChatRoomSerializer(test_chat_room)
    data = serializer.data

    assert data['last_message']['content'] == "Test message"
    assert data['last_message']['sender']['email'] == test_user1.email
    assert data['last_message_sender_id'] == test_user1.id

def test_chat_room_serializer_with_request(test_chat_room, test_user1, test_user2, rf):
    """בדיקת סריאלייזר חדר צ'אט עם קונטקסט של request"""
    # יצירת הודעה
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Test message",
        firebase_id="test_firebase_id"
    )

    request = rf.get('/')
    request.user = test_user2
    serializer = ChatRoomSerializer(test_chat_room, context={'request': request})
    data = serializer.data

    assert data['unread_count'] == 1
    assert data['was_last_message_sent_by_me'] is False

def test_chat_room_serializer_with_last_message(test_chat_room, test_user1):
    """בדיקת סריאלייזר חדר צ'אט עם הודעה אחרונה"""
    # יצירת הודעה אחרונה
    last_message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Last message",
        firebase_id="test_firebase_id_2"
    )

    serializer = ChatRoomSerializer(test_chat_room)
    data = serializer.data

    assert data['last_message']['content'] == "Last message"
    assert data['last_message']['sender']['email'] == test_user1.email
    assert data['last_message_sender_id'] == test_user1.id

def test_chat_room_serializer_with_unread_count(test_chat_room, test_user1, test_user2, rf):
    """בדיקת סריאלייזר חדר צ'אט עם ספירת הודעות שלא נקראו"""
    # הוספת משתמשים לחדר
    test_chat_room.participants.add(test_user1, test_user2)

    # יצירת הודעות שלא נקראו
    Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Unread message 1",
        firebase_id="test_firebase_id_3"
    )

    request = rf.get('/')
    request.user = test_user2
    serializer = ChatRoomSerializer(test_chat_room, context={'request': request})
    data = serializer.data

    assert data['unread_count'] == 1
    assert data['last_message']['content'] == "Unread message 1"
    assert data['last_message']['sender']['email'] == test_user1.email

def test_message_serializer_with_read_status(test_message, test_user2):
    """בדיקת סריאלייזר הודעה עם סטטוס קריאה"""
    from django.utils import timezone
    test_message.read_at = timezone.now()
    test_message.save()

    serializer = MessageSerializer(test_message)
    data = serializer.data

    assert data['is_read'] is True
    assert data['read_at'] is not None 