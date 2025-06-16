from chat.serializers import MessageSerializer
from unittest.mock import Mock
from datetime import datetime


def test_message_serializer_basic_unit():
    """Unit test: serialize basic message fields"""
    user = Mock()
    user.id = 1
    user.email = "user@example.com"
    user.first_name = "User"
    user.last_name = "Test"
    user.user = user

    message = Mock()
    message.id = 1
    message.content = "Hello from unit test"
    message.sender = user
    message.firebase_id = "fake_id_1"
    message.read_at = None
    message.timestamp = datetime.utcnow()

    serializer = MessageSerializer(message)
    data = serializer.data

    assert data['content'] == "Hello from unit test"
    assert data['firebase_id'] == "fake_id_1"
    assert data['read_at'] is None
    assert data['sender']['email'] == "user@example.com"
    assert data['is_sender'] is False

def test_message_serializer_with_read_status_unit():
    """Unit test: serializer reflects read status correctly"""
    user = Mock()
    user.id = 2
    user.email = "user@example.com"
    user.first_name = "User"
    user.last_name = "Test"
    user.user = user

    message = Mock()
    message.id = 2
    message.content = "Already read"
    message.sender = user
    message.firebase_id = "read_id"
    message.read_at = datetime.utcnow()
    message.timestamp = datetime.utcnow()

    serializer = MessageSerializer(message)
    data = serializer.data

    assert data['content'] == "Already read"
    assert data['firebase_id'] == "read_id"
    assert data['read_at'] is not None
    assert data['is_sender'] is False

def test_message_serializer_with_request_unit():
    """Unit test: serializer includes is_sender when context request.user matches"""
    user = Mock()
    user.id = 3
    user.email = "user@example.com"
    user.first_name = "User"
    user.last_name = "Test"

    message = Mock()
    message.id = 3
    message.content = "From me"
    message.sender = user
    message.firebase_id = "context_id"
    message.read_at = None
    message.timestamp = datetime.utcnow()

    # Simulate request object with user
    request = Mock()
    request.user = user

    serializer = MessageSerializer(message, context={'request': request})
    data = serializer.data

    assert data['content'] == "From me"
    assert data['firebase_id'] == "context_id"
    assert data['read_at'] is None
    assert data['is_sender'] is True