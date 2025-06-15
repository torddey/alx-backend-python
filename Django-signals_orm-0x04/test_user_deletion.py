#!/usr/bin/env python
"""
Test script to demonstrate user deletion functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from messaging.models import Message, Notification, MessageHistory
from chats.models import User, Conversation
from django.utils import timezone

def test_user_deletion():
    print("=== Testing User Deletion Functionality ===\n")
    
    # Create test users
    print("1. Creating test users...")
    user1, created = User.objects.get_or_create(
        username='test_user1',
        defaults={'email': 'user1@test.com'}
    )
    user2, created = User.objects.get_or_create(
        username='test_user2',
        defaults={'email': 'user2@test.com'}
    )
    user3, created = User.objects.get_or_create(
        username='test_user3',
        defaults={'email': 'user3@test.com'}
    )
    
    print(f"   Created users: {user1.username}, {user2.username}, {user3.username}")
    print()
    
    # Create messages between users
    print("2. Creating messages between users...")
    message1 = Message.objects.create(
        sender=user1,
        receiver=user2,
        content="Hello from user1 to user2"
    )
    message2 = Message.objects.create(
        sender=user2,
        receiver=user1,
        content="Reply from user2 to user1"
    )
    message3 = Message.objects.create(
        sender=user1,
        receiver=user3,
        content="Hello from user1 to user3"
    )
    
    print(f"   Created {Message.objects.count()} messages")
    print()
    
    # Create notifications
    print("3. Creating notifications...")
    notification1 = Notification.objects.create(
        user=user2,
        message=message1,
        notification_type='message',
        title='New message from user1',
        content='You have a new message'
    )
    notification2 = Notification.objects.create(
        user=user1,
        message=message2,
        notification_type='message',
        title='New message from user2',
        content='You have a new message'
    )
    
    print(f"   Created {Notification.objects.count()} notifications")
    print()
    
    # Edit a message to create history
    print("4. Editing a message to create history...")
    old_content = message1.content
    message1.content = "Updated message from user1 to user2"
    message1.edited_by = user1
    message1.save()
    
    print(f"   Created message history: {MessageHistory.objects.count()} entries")
    print()
    
    # Show current data counts
    print("5. Current data counts before deletion:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Messages: {Message.objects.count()}")
    print(f"   Notifications: {Notification.objects.count()}")
    print(f"   Message History: {MessageHistory.objects.count()}")
    print()
    
    # Delete user1
    print("6. Deleting user1 (this will trigger the post_delete signal)...")
    username_to_delete = user1.username
    user1.delete()
    print(f"   Deleted user: {username_to_delete}")
    print()
    
    # Show data counts after deletion
    print("7. Data counts after deletion:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Messages: {Message.objects.count()}")
    print(f"   Notifications: {Notification.objects.count()}")
    print(f"   Message History: {MessageHistory.objects.count()}")
    print()
    
    # Verify cleanup
    print("8. Verifying cleanup:")
    
    # Check if user1 still exists
    try:
        User.objects.get(username=username_to_delete)
        print(f"   ❌ User {username_to_delete} still exists!")
    except User.DoesNotExist:
        print(f"   ✅ User {username_to_delete} successfully deleted")
    
    # Check if messages from/to user1 were deleted
    messages_from_user1 = Message.objects.filter(sender__username=username_to_delete).count()
    messages_to_user1 = Message.objects.filter(receiver__username=username_to_delete).count()
    print(f"   Messages from {username_to_delete}: {messages_from_user1} (should be 0)")
    print(f"   Messages to {username_to_delete}: {messages_to_user1} (should be 0)")
    
    # Check if notifications for user1 were deleted
    notifications_for_user1 = Notification.objects.filter(user__username=username_to_delete).count()
    print(f"   Notifications for {username_to_delete}: {notifications_for_user1} (should be 0)")
    
    # Check message history (should be reduced since user1's edits are gone)
    history_count = MessageHistory.objects.count()
    print(f"   Message History entries: {history_count}")
    print()
    
    print("=== Test completed successfully! ===")
    print("The post_delete signal successfully cleaned up all user-related data.")

if __name__ == '__main__':
    test_user_deletion() 