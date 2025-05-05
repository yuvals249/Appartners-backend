import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth.models import User, AnonymousUser
from .models import ChatRoom, Message
from firebase_admin import firestore

logger = logging.getLogger('chat')

# Dictionary to track connected users by room
# Format: {room_id: {user_id1, user_id2, ...}}
connected_users = {}

class UserConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for user-specific events.

    This consumer handles real-time updates for a specific user,
    regardless of which room they are currently viewing.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is established.

        Extracts the user_id from the URL and adds the connection to the user-specific group.
        """
        self.user = self.scope['user']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}'

        # Log connection attempt
        logger.info(f"User WebSocket connection attempt for user {self.user_id} by user {self.user}")

        # Check if user is authenticated
        if not self.user.is_authenticated:
            logger.warning(f"User WebSocket connection rejected: User not authenticated")
            await self.close()
            return

        # Check if the user is trying to connect to their own user-specific group
        if int(self.user_id) != self.user.id:
            logger.warning(f"User WebSocket connection rejected: User {self.user.id} tried to connect to user {self.user_id}'s group")
            await self.close()
            return

        logger.info(f"User WebSocket connection accepted for user {self.user_id}")

        # Join user-specific group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

        # Send user presence update to database
        await self.update_user_presence()

    async def disconnect(self, close_code):
        """
        Called when a WebSocket connection is closed.

        Removes the connection from the user-specific group.
        """
        # Leave user-specific group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

        logger.info(f"User {self.user_id} disconnected from user-specific group")

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.

        The UserConsumer doesn't handle any incoming messages from the client,
        it only forwards messages from the server to the client.
        """
        logger.info(f"Received message from user {self.user_id}, but UserConsumer doesn't handle incoming messages")

    async def read_receipt(self, event):
        """
        Called when a read receipt is received from the channel layer.

        Forwards the read receipt to the WebSocket.
        """
        # Send read receipt to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_ids': event['message_ids'],
            'reader_id': event['reader_id'],
            'room_id': event['room_id']
        }))

        logger.info(f"Forwarded read receipt for room {event['room_id']} to user {self.user_id}")

    async def room_update(self, event):
        """
        Called when a room update is received from the channel layer.

        Forwards the room update to the WebSocket.
        """
        # Send room update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'room_update',
            'room': event['room']
        }))

        logger.info(f"Forwarded room update to user {self.user_id}")

    @database_sync_to_async
    def update_user_presence(self):
        """
        Updates the user's presence status.
        """
        from users.models.user_presence import UserPresence

        try:
            # Get or create UserPresence for the user
            presence, created = UserPresence.objects.get_or_create(user=self.user)
            presence.update_presence()
        except Exception as e:
            logger.error(f"Error updating user presence: {str(e)}")

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for chat functionality.

    This consumer handles real-time chat messages and updates, replacing
    the direct Firebase/Firestore usage in the frontend.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is established.

        Extracts the room_id from the URL and adds the connection to the room group.
        Also adds the connection to a user-specific group for receiving updates
        about any room the user is part of.
        """
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        self.user_group_name = f'user_{self.user.id}'

        # Log connection attempt
        logger.info(f"WebSocket connection attempt for room {self.room_id} by user {self.user}")

        # Check if user is authenticated
        if not self.user.is_authenticated:
            logger.warning(f"WebSocket connection rejected: User not authenticated")
            await self.close()
            return

        # Check if user has access to this room
        has_access = await self.user_has_access_to_room(self.room_id, self.user.id)
        if not has_access:
            logger.warning(f"WebSocket connection rejected: User {self.user.id} does not have access to room {self.room_id}")
            await self.close()
            return

        logger.info(f"WebSocket connection accepted for room {self.room_id} by user {self.user.id}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Join user-specific group for receiving updates about any room
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        logger.info(f"User {self.user.id} joined user-specific group {self.user_group_name}")

        await self.accept()

        # Track user connection in the connected_users dictionary
        room_id_str = str(self.room_id)
        if room_id_str not in connected_users:
            connected_users[room_id_str] = set()
        connected_users[room_id_str].add(self.user.id)

        # Log connected users for debugging
        logger.info(f"Connected users in room {self.room_id}: {connected_users[room_id_str]}")

        # Get other participants in the room
        other_participants = await self.get_other_room_participants(self.room_id, self.user.id)

        # Broadcast user presence to other participants if they are connected
        for participant_id in other_participants:
            if room_id_str in connected_users and participant_id in connected_users[room_id_str]:
                # Notify the other user that this user has joined
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_presence',
                        'user_id': self.user.id,
                        'is_online': True
                    }
                )

        # Send user presence update to database
        await self.update_user_presence()

    async def disconnect(self, close_code):
        """
        Called when a WebSocket connection is closed.

        Removes the connection from the room group and user-specific group,
        and updates the connected_users dictionary.
        """
        # Remove user from connected_users dictionary
        room_id_str = str(self.room_id)
        if room_id_str in connected_users and self.user.id in connected_users[room_id_str]:
            connected_users[room_id_str].remove(self.user.id)
            logger.info(f"User {self.user.id} disconnected from room {self.room_id}")

            # If the room is empty, remove it from the dictionary
            if not connected_users[room_id_str]:
                del connected_users[room_id_str]

            # Get other participants in the room
            other_participants = await self.get_other_room_participants(self.room_id, self.user.id)

            # Broadcast user offline status to other participants if they are connected
            for participant_id in other_participants:
                if room_id_str in connected_users and participant_id in connected_users[room_id_str]:
                    # Notify the other user that this user has left
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'user_presence',
                            'user_id': self.user.id,
                            'is_online': False
                        }
                    )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Leave user-specific group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

        logger.info(f"User {self.user.id} left user-specific group {self.user_group_name}")

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.

        Processes the message and broadcasts it to the room group.
        """
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')

            if message_type == 'chat_message':
                # Handle new message
                content = text_data_json.get('content')
                if content:
                    # Save message to database
                    message = await self.save_message(self.room_id, self.user.id, content)

                    # Broadcast message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': {
                                'id': message.id,
                                'content': message.content,
                                'sender_id': message.sender.id,
                                'sender_name': f"{message.sender.first_name} {message.sender.last_name}",
                                'timestamp': message.timestamp.isoformat(),
                                'is_read': message.read_at is not None,
                                'room_id': self.room_id
                            }
                        }
                    )

                    # If message was marked as read immediately, broadcast read receipt
                    if message.read_at is not None:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'read_receipt',
                                'message_ids': [message.id],
                                'reader_id': await self.get_other_participant_id(self.room_id, self.user.id)
                            }
                        )

            elif message_type == 'mark_read':
                # Handle marking messages as read
                message_ids = text_data_json.get('message_ids', [])
                if message_ids:
                    # Mark messages as read in database
                    await self.mark_messages_as_read(message_ids, self.user.id)

                    # Broadcast read status update to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'read_receipt',
                            'message_ids': message_ids,
                            'reader_id': self.user.id
                        }
                    )

            elif message_type == 'typing':
                # Handle typing indicator
                is_typing = text_data_json.get('is_typing', False)

                # Broadcast typing status to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'user_id': self.user.id,
                        'is_typing': is_typing
                    }
                )

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    async def chat_message(self, event):
        """
        Called when a message is received from the room group.

        Sends the message to the WebSocket.
        """
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    async def read_receipt(self, event):
        """
        Called when a read receipt is received from the room group or user-specific group.

        Sends the read receipt to the WebSocket. If the event includes a room_id,
        it means this read receipt was sent to the user-specific group and not the room group,
        so we include the room_id in the message to the client.
        """
        # Prepare the message data
        message_data = {
            'type': 'read_receipt',
            'message_ids': event['message_ids'],
            'reader_id': event['reader_id']
        }

        # If room_id is included, add it to the message
        # This happens when the read receipt is sent to the user-specific group
        if 'room_id' in event:
            message_data['room_id'] = event['room_id']
            logger.info(f"Forwarding read receipt for room {event['room_id']} to client")

        # Send read receipt to WebSocket
        await self.send(text_data=json.dumps(message_data))

    async def typing_indicator(self, event):
        """
        Called when a typing indicator is received from the room group.

        Sends the typing indicator to the WebSocket.
        """
        # Send typing indicator to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing_indicator',
            'user_id': event['user_id'],
            'is_typing': event['is_typing']
        }))

    async def room_update(self, event):
        """
        Called when a room update is received from the room group.

        Sends the room update to the WebSocket.
        """
        # Send room update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'room_update',
            'room': event['room']
        }))

    async def user_presence(self, event):
        """
        Called when a user presence update is received from the room group.

        Sends the user presence update to the WebSocket.
        """
        # Send user presence update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_presence',
            'user_id': event['user_id'],
            'is_online': event['is_online']
        }))

    @database_sync_to_async
    def user_has_access_to_room(self, room_id, user_id):
        """
        Checks if the user has access to the specified room.

        Args:
            room_id: ID of the room to check
            user_id: ID of the user to check

        Returns:
            bool: True if the user has access, False otherwise
        """
        try:
            room = ChatRoom.objects.get(id=room_id)
            return room.participants.filter(id=user_id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, room_id, sender_id, content):
        """
        Saves a new message to the database and Firestore.
        If the recipient is currently viewing the same chat room,
        marks the message as read immediately.

        Args:
            room_id: ID of the room
            sender_id: ID of the sender
            content: Message content

        Returns:
            Message: The created message object
        """
        # Get room and sender
        room = ChatRoom.objects.get(id=room_id)
        sender = User.objects.get(id=sender_id)

        # Check if any recipients are currently viewing this room
        room_id_str = str(room_id)
        other_participants = room.participants.exclude(id=sender_id).values_list('id', flat=True)

        # Determine if message should be marked as read immediately
        mark_as_read = False
        read_at = None

        # If any recipient is currently connected to this room, mark as read
        for participant_id in other_participants:
            if (room_id_str in connected_users and 
                participant_id in connected_users[room_id_str]):
                mark_as_read = True
                read_at = timezone.now()
                logger.info(f"Message will be marked as read immediately because recipient {participant_id} is viewing the room")
                break

        # Create message in Firebase for backward compatibility
        db = firestore.client()
        firebase_data = {
            'room_id': str(room_id),
            'sender_id': str(sender_id),
            'content': content,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'read_at': firestore.SERVER_TIMESTAMP if mark_as_read else None
        }

        firebase_message = db.collection('messages').add(firebase_data)

        # Create message in Django DB
        message = Message.objects.create(
            room=room,
            sender=sender,
            content=content,
            firebase_id=firebase_message[1].id,
            read_at=read_at
        )

        # Update room's last_message_at timestamp
        room.save()

        # If message was marked as read, broadcast read receipt
        if mark_as_read:
            logger.info(f"Broadcasting read receipt for message {message.id}")
            # Note: This will be handled by the caller (receive method)

        return message

    @database_sync_to_async
    def mark_messages_as_read(self, message_ids, user_id):
        """
        Marks messages as read in the database and Firestore.

        Args:
            message_ids: List of message IDs to mark as read
            user_id: ID of the user marking the messages as read
        """
        # Get messages that are not from the current user and are unread
        messages = Message.objects.filter(
            id__in=message_ids,
            read_at__isnull=True
        ).exclude(sender_id=user_id)

        if not messages:
            return

        # Update messages in Django DB
        now = timezone.now()
        messages.update(read_at=now)

        # Update messages in Firebase
        db = firestore.client()
        batch = db.batch()

        for message in messages:
            message_ref = db.collection('messages').document(message.firebase_id)
            batch.update(message_ref, {'read_at': firestore.SERVER_TIMESTAMP})

        batch.commit()

    @database_sync_to_async
    def update_user_presence(self):
        """
        Updates the user's presence status.
        """
        from users.models.user_presence import UserPresence

        try:
            # Get or create UserPresence for the user
            presence, created = UserPresence.objects.get_or_create(user=self.user)
            presence.update_presence()
        except Exception as e:
            logger.error(f"Error updating user presence: {str(e)}")

    @database_sync_to_async
    def get_other_room_participants(self, room_id, user_id):
        """
        Gets the IDs of other participants in the room.

        Args:
            room_id: ID of the room
            user_id: ID of the current user

        Returns:
            list: List of user IDs of other participants in the room
        """
        try:
            room = ChatRoom.objects.get(id=room_id)
            # Get all participants except the current user
            other_participants = room.participants.exclude(id=user_id).values_list('id', flat=True)
            return list(other_participants)
        except ChatRoom.DoesNotExist:
            logger.error(f"Room {room_id} does not exist")
            return []
        except Exception as e:
            logger.error(f"Error getting other room participants: {str(e)}")
            return []

    @database_sync_to_async
    def get_other_participant_id(self, room_id, user_id):
        """
        Gets the ID of the other participant in the room.
        This is a convenience method for 1:1 chat rooms.

        Args:
            room_id: ID of the room
            user_id: ID of the current user

        Returns:
            int: User ID of the other participant in the room
            None: If there is no other participant or an error occurs
        """
        try:
            room = ChatRoom.objects.get(id=room_id)
            # Get the first participant who is not the current user
            other_participant = room.participants.exclude(id=user_id).first()
            return other_participant.id if other_participant else None
        except ChatRoom.DoesNotExist:
            logger.error(f"Room {room_id} does not exist")
            return None
        except Exception as e:
            logger.error(f"Error getting other participant ID: {str(e)}")
            return None
