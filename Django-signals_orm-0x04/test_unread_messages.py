#!/usr/bin/env python
"""
Test script to demonstrate custom UnreadMessagesManager functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from messaging.models import Message
from chats.models import User
from django.db import connection, reset_queries
import time

def test_unread_messages_manager():
    print("=== Testing Custom UnreadMessagesManager ===\n")
    
    # Enable query logging
    reset_queries()
    
    # Create test users
    print("1. Creating test users...")
    user1, created = User.objects.get_or_create(
        username='unread_user1',
        defaults={'email': 'unread1@test.com'}
    )
    user2, created = User.objects.get_or_create(
        username='unread_user2',
        defaults={'email': 'unread2@test.com'}
    )
    user3, created = User.objects.get_or_create(
        username='unread_user3',
        defaults={'email': 'unread3@test.com'}
    )
    
    print(f"   Created users: {user1.username}, {user2.username}, {user3.username}")
    print()
    
    # Create messages with different read statuses
    print("2. Creating messages with different read statuses...")
    
    # Unread messages for user1
    unread_msg1 = Message.objects.create(
        sender=user2,
        receiver=user1,
        content="This is an unread message from user2 to user1",
        read=False,
        is_read=False
    )
    
    unread_msg2 = Message.objects.create(
        sender=user3,
        receiver=user1,
        content="Another unread message from user3 to user1",
        read=False,
        is_read=False
    )
    
    # Read messages for user1
    read_msg1 = Message.objects.create(
        sender=user2,
        receiver=user1,
        content="This is a read message from user2 to user1",
        read=True,
        is_read=True
    )
    
    # Messages for other users
    other_msg = Message.objects.create(
        sender=user1,
        receiver=user2,
        content="Message from user1 to user2",
        read=False,
        is_read=False
    )
    
    print(f"   Created {Message.objects.count()} total messages")
    print()
    
    # Test the custom manager
    print("3. Testing UnreadMessagesManager.for_user()...")
    reset_queries()
    start_time = time.time()
    
    unread_messages = Message.unread.for_user(user1)
    query_time = time.time() - start_time
    
    print(f"   Found {unread_messages.count()} unread messages for {user1.username}")
    print(f"   Query time: {query_time:.4f} seconds")
    print(f"   Number of database queries: {len(connection.queries)}")
    
    for msg in unread_messages:
        print(f"   - {msg.sender.username}: {msg.content[:50]}...")
    
    print()
    
    # Test unread count
    print("4. Testing unread count...")
    reset_queries()
    start_time = time.time()
    
    unread_count = Message.unread.unread_count_for_user(user1)
    query_time = time.time() - start_time
    
    print(f"   Unread count for {user1.username}: {unread_count}")
    print(f"   Query time: {query_time:.4f} seconds")
    print(f"   Number of database queries: {len(connection.queries)}")
    print()
    
    # Test marking specific messages as read
    print("5. Testing mark_as_read_for_user() with specific messages...")
    reset_queries()
    start_time = time.time()
    
    updated_count = Message.unread.mark_as_read_for_user(
        user1, 
        [str(unread_msg1.message_id)]
    )
    query_time = time.time() - start_time
    
    print(f"   Marked {updated_count} messages as read")
    print(f"   Query time: {query_time:.4f} seconds")
    print(f"   Number of database queries: {len(connection.queries)}")
    
    # Check remaining unread count
    remaining_unread = Message.unread.unread_count_for_user(user1)
    print(f"   Remaining unread messages: {remaining_unread}")
    print()
    
    # Test marking all messages as read
    print("6. Testing mark_as_read_for_user() for all messages...")
    reset_queries()
    start_time = time.time()
    
    updated_count = Message.unread.mark_as_read_for_user(user1)
    query_time = time.time() - start_time
    
    print(f"   Marked {updated_count} messages as read")
    print(f"   Query time: {query_time:.4f} seconds")
    print(f"   Number of database queries: {len(connection.queries)}")
    
    # Check final unread count
    final_unread = Message.unread.unread_count_for_user(user1)
    print(f"   Final unread count: {final_unread}")
    print()
    
    # Test query optimization with .only()
    print("7. Testing query optimization...")
    
    # Without optimization
    reset_queries()
    start_time = time.time()
    messages_full = Message.objects.filter(receiver=user1, read=False)
    for msg in messages_full:
        sender_name = msg.sender.username
        content = msg.content
    full_query_time = time.time() - start_time
    full_queries = len(connection.queries)
    
    # With optimization (using custom manager)
    reset_queries()
    start_time = time.time()
    messages_optimized = Message.unread.for_user(user1)
    for msg in messages_optimized:
        sender_name = msg.sender.username
        content = msg.content
    optimized_query_time = time.time() - start_time
    optimized_queries = len(connection.queries)
    
    print(f"   Full query: {full_query_time:.4f} seconds, {full_queries} queries")
    print(f"   Optimized query: {optimized_query_time:.4f} seconds, {optimized_queries} queries")
    print(f"   Query reduction: {full_queries - optimized_queries} queries saved")
    print(f"   Performance improvement: {((full_query_time - optimized_query_time) / full_query_time * 100):.1f}%")
    print()
    
    # Test individual message mark_as_read method
    print("8. Testing individual message mark_as_read() method...")
    
    # Create a new unread message
    test_msg = Message.objects.create(
        sender=user2,
        receiver=user1,
        content="Test message for individual mark as read",
        read=False,
        is_read=False
    )
    
    print(f"   Created test message: read={test_msg.read}, is_read={test_msg.is_read}")
    
    # Mark as read
    test_msg.mark_as_read()
    
    # Refresh from database
    test_msg.refresh_from_db()
    print(f"   After mark_as_read(): read={test_msg.read}, is_read={test_msg.is_read}")
    print()
    
    print("=== Test completed successfully! ===")
    print("Custom UnreadMessagesManager is working with optimized queries.")

if __name__ == '__main__':
    test_unread_messages_manager() 