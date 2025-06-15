import django_filters
from chats.models import Message
import uuid

class MessageFilter(django_filters.FilterSet):
    """
    Filter class for messages, allowing filtering by sender, conversation participants, and time range.
    """
    sender_id = django_filters.UUIDFilter(field_name='sender__user_id')
    participant_id = django_filters.UUIDFilter(field_name='conversation__participants__user_id')
    sent_at__gte = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_at__lte = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['sender_id', 'participant_id', 'sent_at__gte', 'sent_at__lte']