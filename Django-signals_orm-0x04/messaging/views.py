from django.shortcuts import render
from .models import Message

def message_list(request):
    messages = Message.objects.select_related('sender', 'receiver', 'edited_by').prefetch_related('history').all()
    return render(request, 'messaging/message_list.html', {'messages': messages}) 