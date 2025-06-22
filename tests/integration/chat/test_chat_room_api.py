import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from chat.models import ChatRoom
from appartners.utils import generate_jwt


@pytest.mark.django_db
def test_create_chat_room(api_client, test_user1, test_user2, test_token):
    """Test chat room creation"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('chat-room-list')
    data = {
        'participant_id': test_user2.id
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['participants']) == 2
    assert response.data['participants'][0]['id'] == test_user1.id
    assert response.data['participants'][1]['id'] == test_user2.id

@pytest.mark.django_db
def test_create_chat_room_unauthorized(api_client, test_user2):
    """Test chat room creation without authentication"""
    url = reverse('chat-room-list')
    data = {
        'participant_id': test_user2.id
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_list_chat_rooms(api_client, test_user1, test_chat_room, test_token):
    """Test listing chat rooms"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('chat-room-list')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == test_chat_room.id

@pytest.mark.django_db
def test_retrieve_chat_room(api_client, test_user1, test_chat_room, test_token):
    """Test retrieving a chat room"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('chat-room-detail', kwargs={'pk': test_chat_room.id})
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == test_chat_room.id

@pytest.mark.django_db
def test_retrieve_chat_room_unauthorized(api_client, test_chat_room):
    """Test retrieving a chat room without authentication"""
    url = reverse('chat-room-detail', kwargs={'pk': test_chat_room.id})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_retrieve_chat_room_not_participant(api_client, test_user2, test_chat_room):
    """Test retrieving a chat room when not a participant"""
    token = generate_jwt(test_user2)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('chat-room-detail', kwargs={'pk': test_chat_room.id})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_delete_chat_room(api_client, test_user1, test_chat_room, test_token):
    """Test chat room deletion"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('chat-room-detail', kwargs={'pk': test_chat_room.id})
    response = api_client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not ChatRoom.objects.filter(id=test_chat_room.id).exists()

@pytest.mark.django_db
def test_chat_room_messages(api_client, test_user1, test_chat_room, test_token, test_message):
    """Test retrieving messages from a chat room"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('chat-room-messages', kwargs={'pk': test_chat_room.id})
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['content'] == test_message.content

@pytest.mark.django_db
def test_chat_room_unread_count(api_client, test_user1, test_chat_room, test_token, test_message):
    """Test retrieving unread message count"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    url = reverse('chat-room-detail', kwargs={'pk': test_chat_room.id})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['unread_count'] == 0

@pytest.mark.django_db
def test_chat_room_mark_read(api_client, test_user1, test_chat_room, test_token, test_message):
    """Test marking messages as read"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    url = reverse('chat-room-detail', kwargs={'pk': test_chat_room.id})

    response = api_client.patch(url, {'read': True}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['unread_count'] == 0 