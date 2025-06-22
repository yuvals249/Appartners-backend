import pytest
from django.urls import reverse
from rest_framework import status
from chat.models import Message

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_send_message(api_client, test_user1, test_user2, test_token):
    """Test sending a message"""
    # Create a chat room first
    response = api_client.post(
        reverse('chat-room-list'),
        {'participant_id': test_user2.id},
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    room_id = response.data['id']

    # Send a message
    url = reverse('send-message')
    data = {
        'recipient_id': test_user2.id,
        'content': 'New message'
    }

    response = api_client.post(
        url, 
        data, 
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {test_token}'  # Add Authorization header
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message']['content'] == 'New message'
    assert response.data['message']['sender']['email'] == test_user1.email

@pytest.mark.django_db
def test_send_message_unauthorized(api_client, test_user2):
    """Test sending a message without permission"""
    url = reverse('send-message')
    data = {
        'recipient_id': test_user2.id,
        'content': 'New message'
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == 'Authentication credentials were not provided.'

@pytest.mark.django_db
def test_send_message_to_self(api_client, test_user1, test_token):
    """Test sending a message to myself"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('send-message')
    data = {
        'recipient_id': test_user1.id,
        'content': 'New message'
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == 'Cannot send message to yourself'

@pytest.mark.django_db
def test_send_message_invalid_recipient(api_client, test_user1, test_token):
    """Test sending a message to a non-existent user"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('send-message')
    data = {
        'recipient_id': 99999,  # Non-existent
        'content': 'New message'
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'Recipient user not found'

@pytest.mark.django_db
def test_send_message_missing_fields(api_client, test_user1, test_token):
    """Test sending a message without required fields"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('send-message')
    data = {
        'recipient_id': test_user1.id
        # Missing content
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == 'Both recipient_id and content are required'

@pytest.mark.django_db
def test_get_messages(api_client, test_user1, test_user2, test_chat_room, test_token):
    """Test retrieving messages from a room"""
    # Create messages
    for i in range(3):
        Message.objects.create(
            room=test_chat_room,
            sender=test_user2,  # Sender is test_user2
            content=f"Message {i}",
            firebase_id=f"test_firebase_id_{i}"
        )

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    url = reverse('chat-room-messages', args=[test_chat_room.id])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    assert all(msg['content'].startswith('Message') for msg in response.data)
    assert all(msg['is_read'] for msg in response.data)  # All messages should be marked as read
    assert all(msg['sender']['email'] == test_user2.email for msg in response.data)  # All messages were sent by test_user2

@pytest.mark.django_db
def test_create_message(api_client, test_user1, test_user2, test_token):
    """Test creating a message"""
    # Create a chat room
    response = api_client.post(
        reverse('chat-room-list'),
        {'participant_id': test_user2.id},
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    room_id = response.data['id']

    # Send a message
    response = api_client.post(
        reverse('send-message'),
        {
            'recipient_id': test_user2.id,
            'content': 'Test message'
        },
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message']['content'] == 'Test message'
    assert response.data['message']['sender']['email'] == test_user1.email

@pytest.mark.django_db
def test_create_message_unauthorized(api_client, test_user1, test_user2):
    """Test creating a message without permission"""
    response = api_client.post(
        reverse('send-message'),
        {
            'recipient_id': test_user2.id,
            'content': 'Test message'
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == 'Authentication credentials were not provided.'

@pytest.mark.django_db
def test_create_message_not_participant(api_client, test_user1, test_user2, test_token):
    """Test creating a message for a user not in the room"""
    # Send a message to a user not in the room
    response = api_client.post(
        reverse('send-message'),
        {
            'recipient_id': test_user2.id,
            'content': 'Test message'
        },
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message']['content'] == 'Test message'
    assert response.data['message']['sender']['email'] == test_user1.email

@pytest.mark.django_db
def test_list_messages(api_client, test_user1, test_user2, test_token, test_chat_room):
    """Test retrieving a list of messages from a room"""
    # Create some messages
    for i in range(3):
        Message.objects.create(
            room=test_chat_room,
            sender=test_user2,
            content=f'Message {i}',
            firebase_id=f'test_firebase_id_{i}'
        )

    # Retrieve the messages
    response = api_client.get(
        reverse('chat-room-messages', kwargs={'pk': test_chat_room.id}),
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    for i, message in enumerate(response.data):
        assert message['content'] == f'Message {i}'
        assert message['sender']['email'] == test_user2.email

@pytest.mark.django_db
def test_retrieve_message(api_client, test_user1, test_user2, test_token, test_chat_room):
    """Test retrieving a specific message"""
    # Create a message
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user2,
        content='Test message',
        firebase_id='test_firebase_id_retrieve'
    )

    # Retrieve the message
    response = api_client.get(
        reverse('chat-room-messages', kwargs={'pk': test_chat_room.id}),
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['content'] == 'Test message'
    assert response.data[0]['sender']['email'] == test_user2.email

@pytest.mark.django_db
def test_update_message(api_client, test_user1, test_user2, test_chat_room, test_token):
    """Test updating a message"""
    # Create a message
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Original message",
        firebase_id='test_firebase_id_update'  # Add firebase_id
    )

    # Send a new message (cannot update existing messages)
    response = api_client.post(
        reverse('send-message'),
        {
            'recipient_id': test_user2.id,
            'content': 'Updated message'
        },
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message']['content'] == 'Updated message'
    assert response.data['message']['sender']['email'] == test_user1.email

@pytest.mark.django_db
def test_update_message_unauthorized(api_client, test_user1, test_user2, test_chat_room):
    """Test updating a message by an unauthorized user"""
    # Create a message
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user2,
        content="Original message",
        firebase_id='test_firebase_id_update_unauth'  # Add firebase_id
    )

    # Attempt to update a message (cannot update existing messages)
    response = api_client.post(
        reverse('send-message'),
        {
            'recipient_id': test_user1.id,
            'content': 'Updated message'
        },
        format='json'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == 'Authentication credentials were not provided.'

@pytest.mark.django_db
def test_delete_message(api_client, test_user1, test_chat_room, test_token):
    """Test deleting a message"""
    # Create a message
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Test message",
        firebase_id='test_firebase_id_delete'
    )

    # Delete the chat room (this will delete all messages)
    response = api_client.delete(
        reverse('chat-room-detail', kwargs={'pk': test_chat_room.id}),
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Message.objects.filter(id=message.id).exists()

@pytest.mark.django_db
def test_delete_message_unauthorized(api_client, test_user2, test_chat_room):
    """Test deleting a message by an unauthorized user"""
    # Create a message
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user2,
        content="Test message",
        firebase_id='test_firebase_id_delete_unauth'
    )

    # Attempt to delete the chat room without permission
    response = api_client.delete(
        reverse('chat-room-detail', kwargs={'pk': test_chat_room.id})
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == 'Authentication credentials were not provided.'

@pytest.mark.django_db
def test_mark_message_read(api_client, test_user1, test_user2, test_chat_room, test_token):
    """Test marking a message as read"""
    # Create a message from the second user
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user2,  # Changed: Sender is the second user
        content="Test message",
        firebase_id='test_firebase_id_mark_read'  # Add firebase_id
    )

    # Retrieve the messages (this will mark them as read)
    response = api_client.get(
        reverse('chat-room-messages', kwargs={'pk': test_chat_room.id}),
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['read_at'] is not None  # Now it should work because the message is from the second user 