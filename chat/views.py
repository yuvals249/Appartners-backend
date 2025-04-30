from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from firebase_admin import firestore
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.shortcuts import render
from .authentication import JWTAuthentication

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
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer
    
    def get_queryset(self):
        """
        Returns only chat rooms where the current user is a participant.
        Ensures users can only access their own chat rooms.
        """
        return ChatRoom.objects.filter(participants=self.request.user)
    
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
            'is_read': False
        })

        # Create message in Django DB
        message = Message.objects.create(
            room=room,
            sender=request.user,
            content=content,
            firebase_id=firebase_message[1].id,
            is_read=False
        )
        
        # Update room's last_message_at timestamp
        room.save()

        return Response({
            'room': ChatRoomSerializer(room).data,
            'message': MessageSerializer(message).data
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
            is_read=False
        ).exclude(sender=request.user)
        
        # Update messages in Django DB
        unread_messages.update(is_read=True)
        
        # Update messages in Firebase
        if unread_messages.exists():
            db = firestore.client()
            batch = db.batch()
            
            for message in unread_messages:
                message_ref = db.collection('messages').document(message.firebase_id)
                batch.update(message_ref, {'is_read': True})
            
            batch.commit()
        
        # Return all messages
        messages = Message.objects.filter(room=room).order_by('timestamp')
        return Response(MessageSerializer(messages, many=True).data)

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
        return Response(ChatRoomSerializer(room).data)

def test_chat(request):
    """Renders test chat interface (development only)"""
    return render(request, 'chat/test.html')

# Chat visualization at the backend
def chat_view(request):
    """Renders main chat interface"""
    return render(request, 'chat/chat.html')