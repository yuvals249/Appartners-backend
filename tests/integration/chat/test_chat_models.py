import pytest
from django.utils import timezone
from chat.models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_chat_room_str_representation(test_chat_room):
    """Test chat room string representation"""
    expected_str = f'ChatRoom object ({test_chat_room.id})'
    assert str(test_chat_room) == expected_str

@pytest.mark.django_db
def test_chat_room_participants(test_chat_room, test_user1, test_user2):
    """Test chat room participants"""
    assert test_user1 in test_chat_room.participants.all()
    assert test_user2 in test_chat_room.participants.all()
    assert test_chat_room.participants.count() == 2

@pytest.mark.django_db
def test_chat_room_ordering(test_user):
    # Create rooms with different last_message_at times
    room1 = ChatRoom.objects.create(name='Room 1')
    room1.participants.add(test_user)
    room1.last_message_at = timezone.now()
    room1.save()

    room2 = ChatRoom.objects.create(name='Room 2')
    room2.participants.add(test_user)
    room2.last_message_at = timezone.now() + timezone.timedelta(hours=1)
    room2.save()

    # Get rooms ordered by last_message_at
    rooms = ChatRoom.objects.all()
    assert rooms[0] == room2  # Most recent first
    assert rooms[1] == room1

@pytest.mark.django_db
def test_chat_room_auto_timestamps(test_user):
    # Create a new room
    room = ChatRoom.objects.create(name='New Room')
    room.participants.add(test_user)
    
    # Check that timestamps are set
    assert room.created_at is not None
    assert room.last_message_at is not None
    assert room.created_at <= room.last_message_at

@pytest.mark.django_db
def test_chat_room_update_last_message_at(test_chat_room):
    # Get initial timestamp
    initial_timestamp = test_chat_room.last_message_at
    
    # Wait a bit
    import time
    time.sleep(1)
    
    # Update the room
    test_chat_room.name = 'Updated Room'
    test_chat_room.save()
    
    # Check that last_message_at was updated
    test_chat_room.refresh_from_db()
    assert test_chat_room.last_message_at > initial_timestamp 

@pytest.mark.django_db
def test_message_str_representation(test_message):
    """Test message string representation"""
    expected_str = f'{test_message.sender.email}: {test_message.content}'
    assert str(test_message) == expected_str

@pytest.mark.django_db
def test_message_ordering(test_chat_room, test_user):
    # Create messages with different timestamps
    message1 = Message.objects.create(
        room=test_chat_room,
        sender=test_user,
        content='First message',
        firebase_id='test_firebase_id_1'
    )
    
    message2 = Message.objects.create(
        room=test_chat_room,
        sender=test_user,
        content='Second message',
        firebase_id='test_firebase_id_2'
    )
    
    # Get messages ordered by timestamp
    messages = Message.objects.all()
    assert messages[0] == message1  # Oldest first
    assert messages[1] == message2

@pytest.mark.django_db
def test_message_auto_timestamp(test_chat_room, test_user):
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user,
        content='Test message',
        firebase_id='test_firebase_id_auto'
    )
    
    assert message.timestamp is not None
    assert message.read_at is None  # Initially not read

@pytest.mark.django_db
def test_message_mark_as_read(test_message):
    """Test marking message as read"""
    assert test_message.read_at is None
    test_message.read_at = timezone.now()
    test_message.save()
    assert test_message.read_at is not None

@pytest.mark.django_db
def test_message_cascade_delete_room(test_chat_room, test_user):
    # Create a message
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user,
        content='Test message',
        firebase_id='test_firebase_id_cascade'
    )
    
    # Delete the room
    test_chat_room.delete()
    
    # Message should be deleted
    assert not Message.objects.filter(id=message.id).exists()

@pytest.mark.django_db
def test_message_cascade_delete_sender(test_chat_room, test_user):
    # Create a message
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user,
        content='Test message',
        firebase_id='test_firebase_id_cascade_sender'
    )
    
    # Delete the sender
    test_user.delete()
    
    # Message should be deleted
    assert not Message.objects.filter(id=message.id).exists()

@pytest.mark.django_db
def test_message_firebase_id_unique(test_chat_room, test_user):
    # Create first message
    Message.objects.create(
        room=test_chat_room,
        sender=test_user,
        content='First message',
        firebase_id='test_firebase_id_unique'
    )
    
    # Try to create another message with the same firebase_id
    with pytest.raises(Exception):  # Should raise IntegrityError
        Message.objects.create(
            room=test_chat_room,
            sender=test_user,
            content='Second message',
            firebase_id='test_firebase_id_unique'
        ) 

@pytest.mark.django_db
def test_message_creation(test_user1, test_chat_room):
    """Test message creation"""
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Test message",
        firebase_id="test_firebase_id_123"
    )
    
    assert message.room == test_chat_room
    assert message.sender == test_user1
    assert message.content == "Test message"
    assert message.firebase_id == "test_firebase_id_123"
    assert message.read_at is None

@pytest.mark.django_db
def test_chat_room_messages(test_chat_room, test_user1):
    """Test chat room messages"""
    message1 = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Message 1",
        firebase_id="test_firebase_id_1"
    )
    message2 = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Message 2",
        firebase_id="test_firebase_id_2"
    )
    
    messages = test_chat_room.messages.all()
    assert messages.count() == 2
    assert message1 in messages
    assert message2 in messages

@pytest.mark.django_db
def test_chat_room_unread_count(test_chat_room, test_user1, test_user2):
    """Test chat room unread count"""
    Message.objects.create(
        room=test_chat_room,
        sender=test_user2,
        content="Unread message",
        firebase_id="test_firebase_id_123"
    )
    
    unread_count = Message.objects.filter(
        room=test_chat_room,
        read_at__isnull=True
    ).exclude(sender=test_user1).count()
    assert unread_count == 1

@pytest.mark.django_db
def test_chat_room_mark_all_read(test_chat_room, test_user1, test_user2):
    """Test marking all messages as read"""
    Message.objects.create(
        room=test_chat_room,
        sender=test_user2,
        content="Unread message",
        firebase_id="test_firebase_id_123"
    )
    
    unread_count = Message.objects.filter(
        room=test_chat_room,
        read_at__isnull=True
    ).exclude(sender=test_user1).count()
    assert unread_count == 1

    Message.objects.filter(
        room=test_chat_room,
        read_at__isnull=True
    ).exclude(sender=test_user1).update(read_at=timezone.now())

    unread_count = Message.objects.filter(
        room=test_chat_room,
        read_at__isnull=True
    ).exclude(sender=test_user1).count()
    assert unread_count == 0 