import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

def generate_uuid():
    """Generate a unique UUID for model fields."""
    return uuid.uuid4()

class User(AbstractUser):
    """
    Custom user model extending AbstractUser.
    """
    user_id = models.UUIDField(unique=True, default=generate_uuid, editable=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.username

class Conversation(models.Model):
    """
    Conversation model tracks which users are involved in a conversation.
    """
    conversation_id = models.UUIDField(unique=True, default=generate_uuid, editable=False)
    participants = models.ManyToManyField('User', related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"

class Message(models.Model):
    """
    Message model containing sender, conversation, content, and timestamp.
    """
    message_id = models.UUIDField(unique=True, default=generate_uuid, editable=False)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey('User', related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # New fields for message editing
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.username} in Conversation {self.conversation.conversation_id}"

class MessageHistory(models.Model):
    """
    Model to track the history of message edits.
    """
    history_id = models.UUIDField(primary_key=True, default=generate_uuid, editable=False)
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey('User', related_name='message_edits', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-edited_at']

    def __str__(self):
        return f"History for Message {self.message.message_id} edited at {self.edited_at}"