import uuid
from django.db import models
from django.conf import settings
from django.db.models import Q, Prefetch

class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter unread messages for a specific user
    """
    def for_user(self, user):
        """
        Get unread messages for a specific user
        Optimized to retrieve only necessary fields
        """
        return self.filter(
            receiver=user,
            read=False
        ).select_related('sender').only(
            'message_id', 'sender__username', 'content', 'timestamp', 'read'
        ).order_by('-timestamp')
    
    def unread_count_for_user(self, user):
        """
        Get count of unread messages for a user
        """
        return self.filter(
            receiver=user,
            read=False
        ).count()
    
    def mark_as_read_for_user(self, user, message_ids=None):
        """
        Mark messages as read for a user
        If message_ids is provided, mark only those messages
        Otherwise, mark all unread messages for the user
        """
        if message_ids:
            return self.filter(
                receiver=user,
                message_id__in=message_ids,
                read=False
            ).update(read=True)
        else:
            return self.filter(
                receiver=user,
                read=False
            ).update(read=True)

class Message(models.Model):
    """
    Message model for direct messaging between users with threading support
    """
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_direct_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_direct_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read = models.BooleanField(default=False)  # New field for custom manager
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='edited_messages', on_delete=models.SET_NULL)
    
    # Threading support
    parent_message = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    
    # Custom managers
    objects = models.Manager()
    unread = UnreadMessagesManager()
    
    class Meta:
        ordering = ['timestamp']  # Changed to chronological order for threading
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_read']),
            models.Index(fields=['read']),  # New index for read field
            models.Index(fields=['parent_message']),  # New index for threading
        ]
    
    def __str__(self):
        if self.parent_message:
            return f"Reply from {self.sender.username} to {self.receiver.username} at {self.timestamp}"
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"
    
    def mark_as_read(self):
        """Mark this message as read"""
        self.read = True
        self.is_read = True
        self.save(update_fields=['read', 'is_read'])
    
    @property
    def is_reply(self):
        """Check if this message is a reply to another message"""
        return self.parent_message is not None
    
    @property
    def is_thread_start(self):
        """Check if this message starts a thread (has no parent)"""
        return self.parent_message is None
    
    def get_thread_depth(self):
        """Get the depth of this message in the thread"""
        depth = 0
        current = self
        while current.parent_message:
            depth += 1
            current = current.parent_message
        return depth
    
    def get_root_message(self):
        """Get the root message of this thread"""
        current = self
        while current.parent_message:
            current = current.parent_message
        return current
    
    def get_all_replies(self, include_self=False):
        """Get all replies in this thread using recursive query"""
        if include_self:
            return Message.objects.filter(
                Q(message_id=self.message_id) | Q(parent_message=self.message_id)
            ).select_related('sender', 'receiver', 'edited_by').prefetch_related('replies')
        
        return Message.objects.filter(parent_message=self.message_id).select_related(
            'sender', 'receiver', 'edited_by'
        ).prefetch_related('replies')
    
    def get_thread_messages(self):
        """Get all messages in this thread (root + all replies)"""
        root = self.get_root_message()
        return Message.objects.filter(
            Q(message_id=root.message_id) | Q(parent_message=root.message_id)
        ).select_related('sender', 'receiver', 'edited_by').order_by('timestamp')
    
    @classmethod
    def get_threaded_conversations(cls, user1, user2):
        """Get all threaded conversations between two users"""
        return cls.objects.filter(
            Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1)
        ).filter(parent_message__isnull=True).select_related(
            'sender', 'receiver', 'edited_by'
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=cls.objects.select_related('sender', 'receiver', 'edited_by').order_by('timestamp')
            )
        ).order_by('-timestamp')
    
    @classmethod
    def get_user_threads(cls, user):
        """Get all threads where the user is a participant"""
        return cls.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).filter(parent_message__isnull=True).select_related(
            'sender', 'receiver', 'edited_by'
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=cls.objects.select_related('sender', 'receiver', 'edited_by').order_by('timestamp')
            )
        ).order_by('-timestamp')

class Notification(models.Model):
    """
    Notification model to store user notifications
    """
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('mention', 'Mention'),
        ('system', 'System Notification'),
    ]
    
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='message')
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"History for {self.message.message_id} at {self.edited_at}" 