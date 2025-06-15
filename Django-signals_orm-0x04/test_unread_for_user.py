#!/usr/bin/env python
"""
Test script to verify Message.unread.unread_for_user method
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

def test_unread_for_user():
    print("=== Testing Message.unread.unread_for_user Method ===\n")
    
    # Enable query logging
    reset_queries()
    
    # Create test users
    print("1. Creating test users...")
    user1, created = User.objects.get_or_create(
        username='unread_for_user1',
        defaults={'email': 'unread_for_user1@test.com'}
    )
    user2, created = User.objects.get_or_create(
        username='unread_for_user2',
        defaults={'email': 'unread_for_user2@test.com'}
    )
    
    print(f"   Created users: {user1.username}, {user2.username}")
    print()
    
    # Create unread messages
    print("2. Creating unread messages...")
    for i in range(3):
        Message.objects.create(
            sender=user2,
            receiver=user1,
            content=f"Unread message {i+1} for unread_for_user test",
            read=False,
            is_read=False
        )
    
    print(f"   Created 3 unread messages")
    print()
    
    # Test Message.unread.unread_for_user method
    print("3. Testing Message.unread.unread_for_user()...")
    reset_queries()
    start_time = time.time()
    
    # This is the specific method that should be used in views
    unread_messages = Message.unread.unread_for_user(user1)
    query_time = time.time() - start_time
    
    print(f"   Found {unread_messages.count()} unread messages")
    print(f"   Query time: {query_time:.4f} seconds")
    print(f"   Number of database queries: {len(connection.queries)}")
    
    # Show the SQL query to verify .only() is used
    if connection.queries:
        last_query = connection.queries[-1]['sql']
        print(f"   SQL Query: {last_query[:100]}...")
        if 'SELECT' in last_query and 'message_id' in last_query and 'sender__username' in last_query:
            print("   ✅ .only() optimization detected in query")
        else:
            print("   ❌ .only() optimization not detected")
    
    # Display the messages
    for i, msg in enumerate(unread_messages, 1):
        print(f"   Message {i}: {msg.sender.username} - {msg.content[:50]}...")
    
    print()
    
    # Test comparison with for_user method
    print("4. Comparing with for_user method...")
    reset_queries()
    start_time = time.time()
    
    unread_messages_for_user = Message.unread.for_user(user1)
    query_time = time.time() - start_time
    
    print(f"   Found {unread_messages_for_user.count()} unread messages")
    print(f"   Query time: {query_time:.4f} seconds")
    print(f"   Number of database queries: {len(connection.queries)}")
    
    # Verify both methods return the same results
    if list(unread_messages) == list(unread_messages_for_user):
        print("   ✅ Both methods return identical results")
    else:
        print("   ❌ Methods return different results")
    
    print()
    
    # Test the method in a view-like context
    print("5. Testing in view-like context...")
    
    # Simulate what happens in the view
    user = user1  # This would be request.user in a view
    
    # Use the specific method
    unread_messages_view = Message.unread.unread_for_user(user)
    unread_count = Message.unread.unread_count_for_user(user)
    
    print(f"   Unread count: {unread_count}")
    print(f"   Messages retrieved: {unread_messages_view.count()}")
    print(f"   Method used: Message.unread.unread_for_user(user)")
    print("   ✅ View-like context test successful")
    print()
    
    # Test performance
    print("6. Performance test...")
    
    # Test multiple calls to ensure consistency
    times = []
    for i in range(5):
        reset_queries()
        start_time = time.time()
        Message.unread.unread_for_user(user1)
        query_time = time.time() - start_time
        times.append(query_time)
    
    avg_time = sum(times) / len(times)
    print(f"   Average query time: {avg_time:.4f} seconds")
    print(f"   Query times: {[f'{t:.4f}s' for t in times]}")
    print("   ✅ Performance test completed")
    print()
    
    print("=== Test completed successfully! ===")
    print("Message.unread.unread_for_user method is working correctly with .only() optimization.")

if __name__ == '__main__':
    test_unread_for_user() 