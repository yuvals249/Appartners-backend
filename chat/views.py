from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from firebase_admin import firestore
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.shortcuts import render
from django.utils import timezone
from .authentication import JWTAuthentication
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()

class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling chat room operations and messages.

    This ViewSet provides endpoints for managing chat rooms and messages,
    including room creation, message sending, and message retrieval.
    All endpoints require JWT authentication.

    Endpoints:
    - GET /rooms/ - List user's chat rooms
    - POST /rooms/ - Create new chat room
    - GET /rooms/{id}/ - Get specific room
    - POST /rooms/send_message_to_user/ - Send message
    - GET /rooms/{id}/messages/ - Get room messages

    WebSocket Support:
    - Messages are broadcast over WebSockets for real-time updates
    - Read receipts are broadcast over WebSockets
    - Room updates are broadcast over WebSockets
    """

    # Get the channel layer for WebSocket communication
    channel_layer = get_channel_layer()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        """
        Returns only chat rooms where the current user is a participant.
        Ensures users can only access their own chat rooms.
        """
        return ChatRoom.objects.filter(participants=self.request.user)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        Ensures the request is included in the context for all serializers.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_or_create_room(self, user1, user2):
        """
        Helper method to get existing chat room or create new one.

        Args:
            user1: First participant
            user2: Second participant

        Returns:
            ChatRoom: Existing or newly created chat room

        Raises:
            ValueError: If attempting to create room with self
        """
        if user1.id == user2.id:
            raise ValueError("Cannot create a chat room with yourself")

        # Check if room exists with both participants
        existing_room = ChatRoom.objects.filter(participants=user1)\
            .filter(participants=user2)\
            .first()

        if existing_room:
            return existing_room

        # Create new room if none exists
        room = ChatRoom.objects.create()
        room.participants.add(user1, user2)
        return room

    @action(detail=False, methods=['post'])
    def send_message_to_user(self, request):
        """
        Send a message to a user, creating a chat room if needed.

        Handles message creation in both Django DB and Firebase.
        Creates a new chat room if one doesn't exist between the users.

        Request body:
            recipient_id: ID of user to send message to
            content: Message content

        Returns:
            room: Serialized chat room data
            message: Serialized message data
        """
        recipient_id = request.data.get('recipient_id')
        content = request.data.get('content')

        if not recipient_id or not content:
            return Response(
                {'error': 'Both recipient_id and content are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent sending message to yourself
        if int(recipient_id) == request.user.id:
            return Response(
                {'error': 'Cannot send message to yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Recipient user not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get or create chat room
        room = self.get_or_create_room(request.user, recipient)

        # Create message in Firebase for real-time updates
        db = firestore.client()
        firebase_message = db.collection('messages').add({
            'room_id': str(room.id),
            'sender_id': str(request.user.id),
            'content': content,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'read_at': None
        })

        # Create message in Django DB
        message = Message.objects.create(
            room=room,
            sender=request.user,
            content=content,
            firebase_id=firebase_message[1].id,
            read_at=None
        )

        # Update room's last_message_at timestamp
        room.save()

        # Broadcast the new message over WebSockets
        self.broadcast_message(room.id, message)

        # Broadcast room update to reflect the new message to users in the room
        self.broadcast_room_update(room)

        # Broadcast room update to the recipient, even if they're not in this room
        # This ensures the sidebar is updated with the new message
        self.broadcast_room_update_to_user(recipient.id, room)

        return Response({
            'room': ChatRoomSerializer(room, context={'request': request}).data,
            'message': MessageSerializer(message, context={'request': request}).data
        })

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get messages for a specific room and mark unread messages as read.

        Updates read status in both Django DB and Firebase.
        Returns messages sorted by timestamp.

        URL Parameters:
            pk: Room ID

        Returns:
            List of serialized messages
        """
        room = self.get_object()

        # Mark unread messages as read (excluding user's own messages)
        unread_messages = Message.objects.filter(
            room=room,
            read_at__isnull=True
        ).exclude(sender=request.user)

        # Update messages in Django DB
        unread_messages.update(read_at=timezone.now())

        # Update messages in Firebase
        if unread_messages.exists():
            db = firestore.client()
            batch = db.batch()

            for message in unread_messages:
                message_ref = db.collection('messages').document(message.firebase_id)
                batch.update(message_ref, {'read_at': firestore.SERVER_TIMESTAMP})

            batch.commit()

            # Get the IDs of the messages that were marked as read
            message_ids = list(unread_messages.values_list('id', flat=True))

            # Broadcast read receipts over WebSockets
            self.broadcast_read_receipt(room.id, message_ids, request.user.id)

            # Broadcast room update to reflect the read status changes to users in the room
            self.broadcast_room_update(room)

            # Get the senders of the messages that were marked as read
            senders = Message.objects.filter(id__in=message_ids).values_list('sender_id', flat=True).distinct()

            # Broadcast room update to each sender, even if they're not in this room
            # This ensures their sidebar is updated with the read status
            for sender_id in senders:
                if sender_id != request.user.id:  # Don't send to self
                    self.broadcast_room_update_to_user(sender_id, room)

        # Return all messages
        messages = Message.objects.filter(room=room).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new chat room with specified participant.

        Request body:
            participant_id: ID of user to create room with

        Returns:
            Serialized chat room data
        """
        participant_id = request.data.get('participant_id')
        if not participant_id:
            return Response(
                {'error': 'Participant ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Participant not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        room = self.get_or_create_room(request.user, participant)
        return Response(ChatRoomSerializer(room, context={'request': request}).data)

    def broadcast_message(self, room_id, message):
        """
        Broadcasts a new message to all clients connected to the room.

        Args:
            room_id: ID of the room
            message: Message object to broadcast
        """
        room_group_name = f'chat_{room_id}'

        # Prepare message data for WebSocket
        message_data = {
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender.id,
            'sender_name': f"{message.sender.first_name} {message.sender.last_name}",
            'timestamp': message.timestamp.isoformat(),
            'is_read': False,
            'room_id': room_id
        }

        # Broadcast message to room group
        try:
            async_to_sync(self.channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
        except Exception as e:
            logger = logging.getLogger('chat')
            logger.error(f"Error broadcasting message: {str(e)}")
            # Continue without real-time updates if Redis is not available

    def broadcast_read_receipt(self, room_id, message_ids, reader_id):
        """
        Broadcasts a read receipt to all clients connected to the room.
        Also broadcasts to the senders of the messages directly via their user-specific groups.

        Args:
            room_id: ID of the room
            message_ids: List of message IDs that were read
            reader_id: ID of the user who read the messages
        """
        room_group_name = f'chat_{room_id}'

        # Broadcast read receipt to room group
        try:
            async_to_sync(self.channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'read_receipt',
                    'message_ids': message_ids,
                    'reader_id': reader_id
                }
            )
        except Exception as e:
            logger = logging.getLogger('chat')
            logger.error(f"Error broadcasting read receipt to room: {str(e)}")
            # Continue without real-time updates if Redis is not available

        # Also broadcast read receipt directly to the senders of the messages
        # This ensures they receive the update even if they're not currently in the room
        try:
            # Get the senders of the messages
            senders = Message.objects.filter(id__in=message_ids).values_list('sender_id', flat=True).distinct()

            for sender_id in senders:
                if sender_id != reader_id:  # Don't send to self
                    user_group_name = f'user_{sender_id}'

                    # Broadcast read receipt to sender's user-specific group
                    try:
                        async_to_sync(self.channel_layer.group_send)(
                            user_group_name,
                            {
                                'type': 'read_receipt',
                                'message_ids': message_ids,
                                'reader_id': reader_id,
                                'room_id': room_id  # Include room_id so the client knows which room this is for
                            }
                        )
                        logger = logging.getLogger('chat')
                        logger.info(f"Read receipt broadcast to user {sender_id} for messages {message_ids}")
                    except Exception as e:
                        logger = logging.getLogger('chat')
                        logger.error(f"Error broadcasting read receipt to user {sender_id}: {str(e)}")
        except Exception as e:
            logger = logging.getLogger('chat')
            logger.error(f"Error getting message senders: {str(e)}")

    def broadcast_room_update(self, room):
        """
        Broadcasts a room update to all clients connected to the room.

        Args:
            room: ChatRoom object that was updated
        """
        room_group_name = f'chat_{room.id}'

        # Serialize room data for WebSocket
        room_data = ChatRoomSerializer(room, context={'request': None}).data

        # Broadcast room update to room group
        try:
            async_to_sync(self.channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'room_update',
                    'room': room_data
                }
            )
        except Exception as e:
            logger = logging.getLogger('chat')
            logger.error(f"Error broadcasting room update: {str(e)}")
            # Continue without real-time updates if Redis is not available

    def broadcast_room_update_to_user(self, user_id, room):
        """
        Broadcasts a room update to all WebSocket connections of a specific user,
        regardless of which room they are currently viewing.

        This is used to notify users about new messages in rooms they're not currently viewing,
        so they can see updates in the sidebar without refreshing.

        Args:
            user_id: ID of the user to send the update to
            room: ChatRoom object that was updated
        """
        user_group_name = f'user_{user_id}'

        # Serialize room data for WebSocket
        room_data = ChatRoomSerializer(room, context={'request': None}).data

        # Broadcast room update to user's group
        try:
            async_to_sync(self.channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'room_update',
                    'room': room_data
                }
            )
            logger = logging.getLogger('chat')
            logger.info(f"Room update broadcast to user {user_id} for room {room.id}")
        except Exception as e:
            logger = logging.getLogger('chat')
            logger.error(f"Error broadcasting room update to user {user_id}: {str(e)}")
            # Continue without real-time updates if Redis is not available

def test_chat(request):
    """Renders test chat interface (development only)"""
    return render(request, 'chat/test.html')

# Chat visualization at the backend
def chat_view(request):
    """Renders main chat interface"""
    return render(request, 'chat/chat.html')
