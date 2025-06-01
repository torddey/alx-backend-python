from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model extending AbstractUser.
    Add extra fields here if needed in the future.
    """
    # Example: phone_number = models.CharField(max_length=20, blank=True, null=True)
    pass

class Conversation(models.Model):
    """
    Conversation model tracks which users are involved in a conversation.
    """
    participants = models.ManyToManyField('User', related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    """
    Message model containing sender, conversation, content, and timestamp.
    """
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey('User', related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} from {self.sender.username} in Conversation {self.conversation.id}"
