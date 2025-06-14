import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from chat.models import ChatRoom, Message
from django.contrib.auth.models import User
from users.models import UserDetails
from chat.serializers import MessageSerializer
from appartners.utils import generate_jwt

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    """Fixture ליצירת APIClient"""
    return APIClient()

@pytest.fixture
def test_user1():
    """Fixture ליצירת משתמש ראשון לבדיקות"""
    return User.objects.create_user(
        username='user1@example.com',
        email='user1@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User1'
    )

@pytest.fixture
def test_user2():
    """Fixture ליצירת משתמש שני לבדיקות"""
    return User.objects.create_user(
        username='user2@example.com',
        email='user2@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User2'
    )

@pytest.fixture
def test_chat_room(test_user1, test_user2):
    """Fixture ליצירת חדר צ'אט לבדיקות"""
    room = ChatRoom.objects.create(name='Test Room')
    room.participants.add(test_user1, test_user2)
    return room

@pytest.fixture
def test_token(test_user1):
    """Fixture ליצירת טוקן לבדיקות"""
    return generate_jwt(test_user1, 'access')

@pytest.fixture
def test_message(test_chat_room, test_user1):
    return Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content='Test message',
        firebase_id='test_firebase_id_123'
    )

@pytest.mark.django_db
def test_send_message(api_client, test_user1, test_user2, test_token):
    """בדיקת שליחת הודעה"""
    # יצירת חדר צ'אט קודם
    response = api_client.post(
        reverse('chat-room-list'),
        {'participant_id': test_user2.id},
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    room_id = response.data['id']

    # שליחת הודעה
    url = reverse('send-message')
    data = {
        'recipient_id': test_user2.id,
        'content': 'New message'
    }

    response = api_client.post(
        url, 
        data, 
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {test_token}'  # הוספת Authorization header
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message']['content'] == 'New message'
    assert response.data['message']['sender']['email'] == test_user1.email

@pytest.mark.django_db
def test_send_message_unauthorized(api_client, test_user2):
    """בדיקת שליחת הודעה ללא הרשאה"""
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
    """בדיקת שליחת הודעה לעצמי"""
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
    """בדיקת שליחת הודעה למשתמש לא קיים"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('send-message')
    data = {
        'recipient_id': 99999,  # לא קיים
        'content': 'New message'
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'Recipient user not found'

@pytest.mark.django_db
def test_send_message_missing_fields(api_client, test_user1, test_token):
    """בדיקת שליחת הודעה ללא שדות חובה"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    url = reverse('send-message')
    data = {
        'recipient_id': test_user1.id
        # חסר content
    }
    
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == 'Both recipient_id and content are required'

@pytest.mark.django_db
def test_get_messages(api_client, test_user1, test_user2, test_chat_room, test_token):
    """בדיקת קבלת הודעות מחדר"""
    # יצירת הודעות
    for i in range(3):
        Message.objects.create(
            room=test_chat_room,
            sender=test_user2,  # שולח הוא test_user2
            content=f"Message {i}",
            firebase_id=f"test_firebase_id_{i}"
        )

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {test_token}')
    url = reverse('chat-room-messages', args=[test_chat_room.id])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    assert all(msg['content'].startswith('Message') for msg in response.data)
    assert all(msg['is_read'] for msg in response.data)  # כל ההודעות אמורות להיות מסומנות כנקראו
    assert all(msg['sender']['email'] == test_user2.email for msg in response.data)  # כל ההודעות נשלחו על ידי test_user2

@pytest.mark.django_db
def test_create_message(api_client, test_user1, test_user2, test_token):
    """בדיקת יצירת הודעה"""
    # יצירת חדר צ'אט
    response = api_client.post(
        reverse('chat-room-list'),
        {'participant_id': test_user2.id},
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    room_id = response.data['id']

    # שליחת הודעה
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
    """בדיקת יצירת הודעה ללא הרשאה"""
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
    """בדיקת יצירת הודעה למשתמש שלא משתתף בחדר"""
    # שליחת הודעה למשתמש שלא משתתף בחדר
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
    """בדיקת קבלת רשימת הודעות מחדר"""
    # יצירת כמה הודעות
    for i in range(3):
        Message.objects.create(
            room=test_chat_room,
            sender=test_user2,
            content=f'Message {i}',
            firebase_id=f'test_firebase_id_{i}'
        )

    # קבלת ההודעות
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
    """בדיקת קבלת הודעה ספציפית"""
    # יצירת הודעה
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user2,
        content='Test message',
        firebase_id='test_firebase_id_retrieve'
    )

    # קבלת ההודעה
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
    """בדיקת עדכון הודעה"""
    # יצירת הודעה
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Original message",
        firebase_id='test_firebase_id_update'  # הוספת firebase_id
    )

    # שליחת הודעה חדשה (לא ניתן לעדכן הודעות קיימות)
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
    """בדיקת עדכון הודעה על ידי משתמש לא מורשה"""
    # יצירת הודעה
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user2,
        content="Original message",
        firebase_id='test_firebase_id_update_unauth'  # הוספת firebase_id
    )

    # ניסיון לעדכן הודעה (לא ניתן לעדכן הודעות קיימות)
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
    """בדיקת מחיקת הודעה"""
    # יצירת הודעה
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user1,
        content="Test message",
        firebase_id='test_firebase_id_delete'
    )

    # מחיקת חדר הצ'אט (זה ימחק גם את כל ההודעות)
    response = api_client.delete(
        reverse('chat-room-detail', kwargs={'pk': test_chat_room.id}),
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Message.objects.filter(id=message.id).exists()

@pytest.mark.django_db
def test_delete_message_unauthorized(api_client, test_user2, test_chat_room):
    """בדיקת מחיקת הודעה על ידי משתמש לא מורשה"""
    # יצירת הודעה
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user2,
        content="Test message",
        firebase_id='test_firebase_id_delete_unauth'
    )

    # ניסיון למחוק חדר צ'אט ללא הרשאה
    response = api_client.delete(
        reverse('chat-room-detail', kwargs={'pk': test_chat_room.id})
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == 'Authentication credentials were not provided.'

@pytest.mark.django_db
def test_mark_message_read(api_client, test_user1, test_user2, test_chat_room, test_token):
    """בדיקת סימון הודעה כנקראה"""
    # יצירת הודעה מהמשתמש השני
    message = Message.objects.create(
        room=test_chat_room,
        sender=test_user2,  # שינוי: שולח הוא המשתמש השני
        content="Test message",
        firebase_id='test_firebase_id_mark_read'  # הוספת firebase_id
    )

    # קבלת ההודעות (זה יסמן אותן כנקראו)
    response = api_client.get(
        reverse('chat-room-messages', kwargs={'pk': test_chat_room.id}),
        HTTP_AUTHORIZATION=f'Bearer {test_token}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['read_at'] is not None  # עכשיו זה אמור לעבוד כי ההודעה היא מהמשתמש השני 