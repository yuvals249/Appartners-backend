from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    """
    Represents a chat room where users can exchange messages.

    This model stores information about chat conversations between users.
    Each chat room can have multiple participants and maintains a record
    of when it was created and when the last message was sent.

    Attributes:
        name (CharField): Name identifier for the chat room (255 chars max)
        participants (ManyToManyField): Users participating in this chat room
            - Creates a reverse relation 'chat_rooms' on User model
        created_at (DateTimeField): Timestamp when the room was created
            - Automatically set when the room is created
        last_message_at (DateTimeField): Timestamp of the most recent message
            - Automatically updated whenever the room is saved
    """
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta configuration for ChatRoom model.
        Orders chat rooms by most recent message first.
        """
        ordering = ['-last_message_at']


class Message(models.Model):
    """
    Represents an individual message within a chat room.

    This model stores the actual messages sent between users, including
    metadata about the sender, timing, and read status. It also maintains
    synchronization with Firebase through a unique identifier.

    Attributes:
        room (ForeignKey): Reference to the ChatRoom this message belongs to
            - Deleting a room will delete all its messages (CASCADE)
            - Creates a reverse relation 'messages' on ChatRoom model
        sender (ForeignKey): The User who sent this message
            - Deleting a user will delete their messages (CASCADE)
        content (TextField): The actual message content
            - Unlimited length text field
        timestamp (DateTimeField): When the message was sent
            - Automatically set when message is created
        firebase_id (CharField): Unique identifier for Firebase sync
            - Must be unique across all messages
            - Used for real-time updates with Firebase
        read_at (DateTimeField): Timestamp when the message was read
            - Null if the message hasn't been read yet
    """
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    firebase_id = models.CharField(max_length=255, unique=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """
        Meta configuration for Message model.
        Orders messages by timestamp, showing oldest first.
        """
        ordering = ['timestamp']

    def __str__(self):
        """
        String representation of a Message.

        Returns:
            str: Format: "username: first 50 chars of message"
                Example: "john_doe: Hello, how are you?"
        """
        return f'{self.sender.username}: {self.content[:50]}'
