from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Message, MessageHistory

@receiver(pre_save, sender=Message)
def log_message_history(sender, instance, **kwargs):
    """
    Signal to log message history before saving updates.
    """
    if instance.pk:  # Only for existing messages (updates)
        try:
            # Get the original message from database
            original_message = Message.objects.get(pk=instance.pk)
            
            # Check if content has changed
            if original_message.content != instance.content:
                
                # Create history entry
                MessageHistory.objects.create(
                    message=instance,
                    old_content=original_message.content,
                    edited_by=instance.sender  # Assuming the sender is editing
                )
                
                # Mark message as edited
                instance.edited = True
                instance.edited_at = timezone.now()
                
        except Message.DoesNotExist:
            # This shouldn't happen for updates, but handle gracefully
            pass 