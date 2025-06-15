from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Message, Notification, MessageHistory

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