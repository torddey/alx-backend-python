# Message Editing Features

This document describes the message editing functionality that has been implemented in the messaging application.

## Overview

The message editing system allows users to:
- Edit their own messages
- Track edit history automatically
- View previous versions of edited messages
- See when and by whom messages were edited

## Features Implemented

### 1. Message Model Enhancements

The `Message` model now includes:
- `edited` (BooleanField): Indicates if the message has been edited
- `edited_at` (DateTimeField): Timestamp of the last edit
- `message_id` (UUIDField): Unique identifier for the message

### 2. MessageHistory Model

A new `MessageHistory` model tracks edit history:
- `history_id` (UUIDField): Primary key
- `message` (ForeignKey): Reference to the edited message
- `old_content` (TextField): Previous content before the edit
- `edited_at` (DateTimeField): When the edit occurred
- `edited_by` (ForeignKey): User who made the edit

### 3. Automatic History Tracking

Django signals automatically:
- Detect when a message's content changes
- Save the old content to MessageHistory
- Update the message's `edited` and `edited_at` fields
- Track who made the edit

### 4. API Endpoints

#### Message Editing
- `PUT /api/messages/{message_id}/` - Edit a message
- `GET /api/messages/{message_id}/` - Get message details with edit info

#### Message History
- `GET /api/messages/{message_id}/history/` - Get edit history for a message

## Usage Examples

### 1. Editing a Message

```bash
# Edit a message
curl -X PUT http://localhost:8000/api/messages/{message_id}/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated message content"}'
```

Response:
```json
{
  "message_id": "uuid",
  "conversation": "conversation_id",
  "sender": {
    "user_id": "uuid",
    "username": "user",
    "first_name": "User",
    "last_name": "Name",
    "email": "user@example.com"
  },
  "content": "Updated message content",
  "timestamp": "2025-06-15T21:21:13.776907Z",
  "edited": true,
  "edited_at": "2025-06-15T21:21:13.776907Z",
  "history": [
    {
      "history_id": "uuid",
      "old_content": "Original message content",
      "edited_at": "2025-06-15T21:21:13.776907Z",
      "edited_by": {
        "user_id": "uuid",
        "username": "user",
        "first_name": "User",
        "last_name": "Name",
        "email": "user@example.com"
      }
    }
  ]
}
```

### 2. Viewing Message History

```bash
# Get message edit history
curl -X GET http://localhost:8000/api/messages/{message_id}/history/ \
  -H "Authorization: Bearer {token}"
```

Response:
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "history_id": "uuid",
      "old_content": "First version of the message",
      "edited_at": "2025-06-15T21:20:00.000000Z",
      "edited_by": {
        "user_id": "uuid",
        "username": "user",
        "first_name": "User",
        "last_name": "Name",
        "email": "user@example.com"
      }
    },
    {
      "history_id": "uuid",
      "old_content": "Second version of the message",
      "edited_at": "2025-06-15T21:21:00.000000Z",
      "edited_by": {
        "user_id": "uuid",
        "username": "user",
        "first_name": "User",
        "last_name": "Name",
        "email": "user@example.com"
      }
    }
  ]
}
```

## Database Schema

### Message Table
```sql
CREATE TABLE chats_message (
    id INTEGER PRIMARY KEY,
    message_id UUID UNIQUE NOT NULL,
    conversation_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    edited BOOLEAN DEFAULT FALSE,
    edited_at DATETIME NULL,
    FOREIGN KEY (conversation_id) REFERENCES chats_conversation(id),
    FOREIGN KEY (sender_id) REFERENCES chats_user(id)
);
```

### MessageHistory Table
```sql
CREATE TABLE chats_messagehistory (
    history_id UUID PRIMARY KEY,
    message_id INTEGER NOT NULL,
    old_content TEXT NOT NULL,
    edited_at DATETIME NOT NULL,
    edited_by_id INTEGER NOT NULL,
    FOREIGN KEY (message_id) REFERENCES chats_message(id),
    FOREIGN KEY (edited_by_id) REFERENCES chats_user(id)
);
```

## Implementation Details

### 1. Django Signals

The `signals.py` file contains a `pre_save` signal that:
- Triggers before a message is saved
- Compares old and new content
- Creates history entries for changes
- Updates edit metadata

### 2. Permissions

- Only message senders can edit their own messages
- All conversation participants can view message history
- Proper authentication and authorization enforced

### 3. Serializers

- `MessageSerializer`: Includes edit information and history
- `MessageHistorySerializer`: Serializes history entries
- `MessageBasicSerializer`: Lightweight version for lists

### 4. Views

- `MessageViewSet`: Handles CRUD operations and history endpoint
- Automatic filtering by conversation participation
- Pagination for history results

## Testing

Run the test script to verify functionality:

```bash
python test_message_editing.py
```

This script demonstrates:
1. Creating users and conversations
2. Sending messages
3. Editing messages
4. Viewing edit history
5. Multiple edits tracking

## Security Considerations

1. **Authentication**: All endpoints require valid JWT tokens
2. **Authorization**: Users can only edit their own messages
3. **Data Integrity**: History is automatically maintained
4. **Audit Trail**: All edits are tracked with timestamps and user info

## Future Enhancements

Potential improvements:
1. Edit time limits (e.g., only allow edits within 5 minutes)
2. Edit notifications to other participants
3. Rich text editing support
4. Edit conflict resolution
5. Bulk edit operations
6. Edit statistics and analytics

## Troubleshooting

### Common Issues

1. **History not being created**: Check that the signal is properly registered in `apps.py`
2. **Permission errors**: Ensure the user is the message sender
3. **UUID conflicts**: Verify UUID generation is working correctly

### Debug Commands

```python
# Check if signals are working
from chats.models import Message
message = Message.objects.get(message_id='your-message-id')
print(f"Edited: {message.edited}")
print(f"History count: {message.history.count()}")

# View all history entries
for entry in message.history.all():
    print(f"Old content: {entry.old_content}")
    print(f"Edited at: {entry.edited_at}")
    print(f"Edited by: {entry.edited_by.username}")
```

## API Documentation

For complete API documentation, see the Django REST Framework browsable API at:
`http://localhost:8000/api/` 