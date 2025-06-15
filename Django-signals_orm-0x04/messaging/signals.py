from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
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

@receiver(pre_delete, sender=User)
def cleanup_user_data_before_delete(sender, instance, **kwargs):
    """
    Clean up all user-related data before a user is deleted
    This signal ensures that all messages, notifications, and message histories
    associated with the user are properly removed using delete() methods
    """
    user_id = instance.user_id
    username = instance.username
    
    # Log the cleanup process
    print(f"Starting cleanup for user: {username} (ID: {user_id})")
    
    # Count what will be deleted (for logging purposes)
    messages_to_delete = Message.objects.filter(
        models.Q(sender=instance) | models.Q(receiver=instance)
    )
    notifications_to_delete = Notification.objects.filter(user=instance)
    history_to_clean = MessageHistory.objects.filter(edited_by=instance)
    
    message_count = messages_to_delete.count()
    notification_count = notifications_to_delete.count()
    history_count = history_to_clean.count()
    
    print(f"Found {message_count} messages, {notification_count} notifications, {history_count} history entries to clean up")
    
    # Delete messages (this will cascade to related notifications and history)
    if message_count > 0:
        print(f"Deleting {message_count} messages...")
        messages_to_delete.delete()
    
    # Delete any remaining notifications not caught by cascade
    if notification_count > 0:
        print(f"Deleting {notification_count} notifications...")
        notifications_to_delete.delete()
    
    # Clean up message history entries where user was the editor
    if history_count > 0:
        print(f"Cleaning up {history_count} message history entries...")
        # Option 1: Delete the history entries completely
        history_to_clean.delete()
        # Option 2: Set edited_by to NULL (uncomment if you prefer this approach)
        # history_to_clean.update(edited_by=None)
    
    print(f"Cleanup completed for user {username}")

@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """
    Log user deletion after it's completed
    """
    print(f"User {instance.username} has been successfully deleted")
    print("All related data has been cleaned up") 