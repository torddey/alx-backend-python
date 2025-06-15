from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Message, Notification, MessageHistory
from django.db import models

# Import User model
User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal to automatically create a notification when a new message is created
    """
    if created:
        # Create notification for the receiver
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='message',
            title=f'New message from {instance.sender.username}',
            content=f'You have received a new message: "{instance.content[:50]}{"..." if len(instance.content) > 50 else ""}"'
        )

@receiver(post_save, sender=Message)
def update_message_notification(sender, instance, created, **kwargs):
    """
    Signal to update notification when message is read
    """
    if not created and instance.is_read:
        # Mark related notifications as read
        Notification.objects.filter(
            user=instance.receiver,
            message=instance,
            notification_type='message'
        ).update(is_read=True)

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if not instance._state.adding:
        try:
            old = Message.objects.get(pk=instance.pk)
        except Message.DoesNotExist:
            return
        if old.content != instance.content:
            MessageHistory.objects.create(
                message=instance,
                old_content=old.content,
                edited_by=getattr(instance, 'edited_by', None)
            )
            instance.edited = True

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up all user-related data when a user is deleted
    This signal ensures that all messages, notifications, and message histories
    associated with the deleted user are properly removed
    """
    user_id = instance.user_id
    
    # Log the cleanup process
    print(f"Cleaning up data for deleted user: {instance.username} (ID: {user_id})")
    
    # Note: Most cleanup is handled automatically by CASCADE relationships
    # This signal is mainly for logging and any additional cleanup logic
    
    # Count what was deleted (for logging purposes)
    deleted_messages = Message.objects.filter(
        models.Q(sender=instance) | models.Q(receiver=instance)
    ).count()
    
    deleted_notifications = Notification.objects.filter(user=instance).count()
    
    # MessageHistory entries with edited_by=instance will be set to NULL due to SET_NULL
    # We can optionally delete them completely if desired
    deleted_history = MessageHistory.objects.filter(edited_by=instance).count()
    
    print(f"Cleanup completed for user {instance.username}:")
    print(f"  - {deleted_messages} messages deleted")
    print(f"  - {deleted_notifications} notifications deleted")
    print(f"  - {deleted_history} message history entries affected") 