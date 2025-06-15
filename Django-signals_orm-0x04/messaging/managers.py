from django.db import models

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