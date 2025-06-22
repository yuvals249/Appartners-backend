import pytest
from unittest.mock import Mock, AsyncMock
from chat.consumers import ChatConsumer


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_connect():
    """Test successful WebSocket connection"""
    consumer = ChatConsumer()
    consumer.scope = {
        'type': 'websocket',
        'user': Mock(id=1, is_authenticated=True),
        'url_route': {'kwargs': {'room_id': '1'}}
    }
    consumer.channel_layer = AsyncMock()
    consumer.channel_name = 'test_channel'
    consumer.room_group_name = 'chat_1'
    consumer.user_group_name = 'user_1'
    consumer.base_send = AsyncMock()
    
    # Mock the user_has_access_to_room method
    consumer.user_has_access_to_room = AsyncMock(return_value=True)
    
    await consumer.connect()
    
    assert consumer.channel_layer.group_add.called
    assert consumer.room_id == '1'

@pytest.mark.asyncio
async def test_disconnect():
    """Test WebSocket disconnection"""
    consumer = ChatConsumer()
    consumer.room_id = '1'
    consumer.channel_layer = AsyncMock()
    consumer.channel_name = 'test_channel'
    consumer.room_group_name = 'chat_1'
    consumer.user_group_name = 'user_1'
    consumer.user = Mock(id=1)
    
    # Mock get_other_room_participants
    consumer.get_other_room_participants = AsyncMock(return_value=[])
    
    await consumer.disconnect(1000)
    
    assert consumer.channel_layer.group_discard.called


@pytest.mark.asyncio
async def test_chat_message():
    """Test sending a message to the WebSocket"""
    consumer = ChatConsumer()
    consumer.send = AsyncMock()
    
    message = {
        'message': 'Test message',
        'sender': {'id': 1, 'email': 'test@example.com'}
    }
    
    # Mock the send method to handle text_data parameter
    async def mock_send(*args, **kwargs):
        return {'type': 'websocket.send', 'text': kwargs.get('text_data')}
    consumer.send.side_effect = mock_send
    
    await consumer.chat_message(message)
    assert consumer.send.called
    send_args = consumer.send.call_args[1]  # Using kwargs
    assert send_args['text_data'] is not None

@pytest.mark.asyncio
async def test_unauthorized_connection():
    """Test connection rejection for unauthorized users"""
    consumer = ChatConsumer()
    consumer.scope = {
        'type': 'websocket',
        'user': Mock(is_authenticated=False),
        'url_route': {'kwargs': {'room_id': '1'}}
    }
    
    with pytest.raises(Exception):
        await consumer.connect() 