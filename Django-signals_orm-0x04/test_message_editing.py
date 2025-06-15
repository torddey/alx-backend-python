#!/usr/bin/env python
"""
Test script to demonstrate message editing functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from messaging.models import Message, MessageHistory
from chats.models import User
from django.utils import timezone

def test_message_editing():
    print("=== Testing Message Editing Functionality ===\n")
    
    # Create test users if they don't exist
    sender, created = User.objects.get_or_create(
        username='test_sender',
        defaults={'email': 'sender@test.com'}
    )
    receiver, created = User.objects.get_or_create(
        username='test_receiver', 
        defaults={'email': 'receiver@test.com'}
    )
    
    # Create a new message
    print("1. Creating a new message...")
    message = Message.objects.create(
        sender=sender,
        receiver=receiver,
        content="Hello! This is my first message."
    )
    print(f"   Message created: {message.content}")
    print(f"   Message ID: {message.message_id}")
    print(f"   Edited: {message.edited}")
    print()
    
    # Edit the message
    print("2. Editing the message...")
    old_content = message.content
    message.content = "Hello! This is my updated message with corrections."
    message.edited_by = sender
    message.save()
    print(f"   Original content: {old_content}")
    print(f"   New content: {message.content}")
    print(f"   Edited: {message.edited}")
    print(f"   Edited by: {message.edited_by.username if message.edited_by else 'Unknown'}")
    print()
    
    # Check message history
    print("3. Checking message history...")
    history_entries = MessageHistory.objects.filter(message=message)
    print(f"   Number of history entries: {history_entries.count()}")
    
    for i, history in enumerate(history_entries, 1):
        print(f"   History {i}:")
        print(f"     Old content: {history.old_content}")
        print(f"     Edited at: {history.edited_at}")
        print(f"     Edited by: {history.edited_by.username if history.edited_by else 'Unknown'}")
    print()
    
    # Edit the message again
    print("4. Editing the message again...")
    old_content = message.content
    message.content = "Hello! This is my final message with all corrections."
    message.edited_by = sender
    message.save()
    print(f"   Previous content: {old_content}")
    print(f"   Final content: {message.content}")
    print()
    
    # Check updated history
    print("5. Updated message history...")
    history_entries = MessageHistory.objects.filter(message=message).order_by('-edited_at')
    print(f"   Total history entries: {history_entries.count()}")
    
    for i, history in enumerate(history_entries, 1):
        print(f"   History {i}:")
        print(f"     Old content: {history.old_content}")
        print(f"     Edited at: {history.edited_at}")
        print(f"     Edited by: {history.edited_by.username if history.edited_by else 'Unknown'}")
    print()
    
    print("=== Test completed successfully! ===")
    print("You can now visit http://localhost:8000/messaging/messages/ to see the UI")

if __name__ == '__main__':
    test_message_editing() 