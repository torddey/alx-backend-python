from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),
]

# This configuration will create the following URL patterns:

# Conversation endpoints:
# GET    /api/conversations/                           - List all conversations for the user
# POST   /api/conversations/                           - Create a new conversation
# GET    /api/conversations/{id}/                      - Get specific conversation with messages
# PUT    /api/conversations/{id}/                      - Update conversation
# PATCH  /api/conversations/{id}/                      - Partially update conversation
# DELETE /api/conversations/{id}/                      - Delete conversation
# GET    /api/conversations/{id}/messages/             - Get paginated messages for conversation
# POST   /api/conversations/{id}/add-participant/      - Add participant to conversation
# POST   /api/conversations/{id}/remove-participant/   - Remove participant from conversation

# Message endpoints:
# GET    /api/messages/                                - List all messages for the user
# POST   /api/messages/                                - Send a new message
# GET    /api/messages/{id}/                           - Get specific message
# PUT    /api/messages/{id}/                           - Update message (only by sender)
# PATCH  /api/messages/{id}/                           - Partially update message (only by sender)
# DELETE /api/messages/{id}/                           - Delete message (only by sender)
# GET    /api/messages/conversation/{conversation_id}/ - Get messages by conversation
# GET    /api/messages/search/?q=query                 - Search messages by content