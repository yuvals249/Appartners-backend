import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from chat.models import ChatRoom, Message
from users.models import UserDetails
from django.test import TestCase
from appartners.utils import generate_jwt
import json

@pytest.fixture
def api_client():
    """Fixture ליצירת APIClient"""
    return APIClient()

@pytest.fixture
def test_user1(db):
    """Fixture ליצירת משתמש ראשון לבדיקות"""
    user = User.objects.create_user(
        username="user1@example.com",
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
        username="user2@example.com",
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
def test_token(db, test_user1):
    """Fixture ליצירת טוקן JWT לבדיקות"""
    return generate_jwt(test_user1, 'access')

def test_create_chat_room(api_client, test_user1, test_user2, test_token):
    """בדיקת יצירת חדר צ'אט"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('chat-room-list')
    data = {
        'participant_id': test_user2.id
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['participants'][0]['email'] == test_user1.email
    assert response.data['participants'][1]['email'] == test_user2.email

def test_create_chat_room_unauthorized(api_client, test_user2):
    """בדיקת יצירת חדר צ'אט ללא הרשאה"""
    url = reverse('chat-room-list')
    data = {
        'participant_id': test_user2.id
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == 'Authentication credentials were not provided.'

def test_list_chat_rooms(api_client, test_user1, test_chat_room, test_token):
    """בדיקת רשימת חדרי צ'אט"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('chat-room-list')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == test_chat_room.id

def test_retrieve_chat_room(api_client, test_user1, test_chat_room, test_token):
    """בדיקת קבלת פרטי חדר צ'אט"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('chat-room-detail', args=[test_chat_room.id])
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == test_chat_room.id
    assert len(response.data['participants']) == 2

def test_delete_chat_room(api_client, test_user1, test_chat_room, test_token):
    """בדיקת מחיקת חדר צ'אט"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('chat-room-detail', args=[test_chat_room.id])
    response = api_client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not ChatRoom.objects.filter(id=test_chat_room.id).exists()

def test_chat_room_messages(api_client, test_user1, test_chat_room, test_token):
    """בדיקת קבלת הודעות חדר צ'אט"""
    # יצירת כמה הודעות
    for i in range(3):
        Message.objects.create(
            room=test_chat_room,
            sender=test_user1,
            content=f"Message {i}",
            firebase_id=f"test_firebase_id_{i}"
        )
    
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    url = reverse('chat-room-messages', args=[test_chat_room.id])
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    assert all(msg['content'].startswith('Message') for msg in response.data)

def test_chat_room_unread_count(api_client, test_user1, test_user2, test_chat_room, test_token):
    """בדיקת ספירת הודעות שלא נקראו"""
    # יצירת הודעות שלא נקראו
    for i in range(3):
        Message.objects.create(
            room=test_chat_room,
            sender=test_user2,
            content=f"Unread message {i}",
            firebase_id=f"test_firebase_id_{i}"
        )
    
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    url = reverse('chat-room-detail', args=[test_chat_room.id])
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['unread_count'] == 3

def test_chat_room_mark_read(api_client, test_user1, test_user2, test_chat_room, test_token):
    """בדיקת סימון הודעות כנקראו"""
    # יצירת הודעות שלא נקראו
    messages = []
    for i in range(3):
        message = Message.objects.create(
            room=test_chat_room,
            sender=test_user2,
            content=f"Unread message {i}",
            firebase_id=f"test_firebase_id_{i}"
        )
        messages.append(message)
    
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    url = reverse('chat-room-messages', args=[test_chat_room.id])
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert all(msg['is_read'] for msg in response.data) 