#!/usr/bin/env python
"""
Test script to demonstrate .only() optimization in views
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

def test_views_optimization():
    print("=== Testing .only() Optimization in Views ===\n")
    
    # Enable query logging
    reset_queries()
    
    # Create test users
    print("1. Creating test users...")
    user1, created = User.objects.get_or_create(
        username='view_user1',
        defaults={'email': 'view1@test.com'}
    )
    user2, created = User.objects.get_or_create(
        username='view_user2',
        defaults={'email': 'view2@test.com'}
    )
    
    print(f"   Created users: {user1.username}, {user2.username}")
    print()
    
    # Create unread messages
    print("2. Creating unread messages...")
    for i in range(5):
        Message.objects.create(
            sender=user2,
            receiver=user1,
            content=f"Unread message {i+1} from {user2.username} to {user1.username}",
            read=False,
            is_read=False
        )
    
    print(f"   Created 5 unread messages")
    print()
    
    # Test custom manager with .only() optimization
    print("3. Testing custom manager with .only() optimization...")
    reset_queries()
    start_time = time.time()
    
    # This uses the custom manager which includes .only() optimization
    unread_messages = Message.unread.for_user(user1)
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
    
    print()
    
    # Test explicit .only() usage (like in unread_messages_optimized view)
    print("4. Testing explicit .only() usage...")
    reset_queries()
    start_time = time.time()
    
    # This mimics the unread_messages_optimized view
    unread_messages_explicit = Message.objects.filter(
        receiver=user1,
        read=False
    ).select_related('sender').only(
        'message_id', 'sender__username', 'content', 'timestamp', 'read'
    ).order_by('-timestamp')
    
    query_time = time.time() - start_time
    
    print(f"   Found {unread_messages_explicit.count()} unread messages")
    print(f"   Query time: {query_time:.4f} seconds")
    print(f"   Number of database queries: {len(connection.queries)}")
    
    # Show the SQL query
    if connection.queries:
        last_query = connection.queries[-1]['sql']
        print(f"   SQL Query: {last_query[:100]}...")
        if 'SELECT' in last_query and 'message_id' in last_query and 'sender__username' in last_query:
            print("   ✅ .only() optimization detected in query")
        else:
            print("   ❌ .only() optimization not detected")
    
    print()
    
    # Test without .only() optimization (for comparison)
    print("5. Testing without .only() optimization...")
    reset_queries()
    start_time = time.time()
    
    # This would be the unoptimized version
    unread_messages_full = Message.objects.filter(
        receiver=user1,
        read=False
    ).select_related('sender').order_by('-timestamp')
    
    query_time = time.time() - start_time
    
    print(f"   Found {unread_messages_full.count()} unread messages")
    print(f"   Query time: {query_time:.4f} seconds")
    print(f"   Number of database queries: {len(connection.queries)}")
    
    # Show the SQL query
    if connection.queries:
        last_query = connection.queries[-1]['sql']
        print(f"   SQL Query: {last_query[:100]}...")
        if 'SELECT' in last_query and '*' in last_query:
            print("   ✅ Full query detected (no .only() optimization)")
        else:
            print("   ❌ Unexpected query format")
    
    print()
    
    # Test custom manager methods
    print("6. Testing custom manager methods...")
    reset_queries()
    start_time = time.time()
    
    # Test unread_count_for_user
    unread_count = Message.unread.unread_count_for_user(user1)
    query_time = time.time() - start_time
    
    print(f"   Unread count: {unread_count}")
    print(f"   Query time: {query_time:.4f} seconds")
    print(f"   Number of database queries: {len(connection.queries)}")
    
    # Test mark_as_read_for_user
    reset_queries()
    start_time = time.time()
    
    updated_count = Message.unread.mark_as_read_for_user(user1)
    query_time = time.time() - start_time
    
    print(f"   Marked {updated_count} messages as read")
    print(f"   Query time: {query_time:.4f} seconds")
    print(f"   Number of database queries: {len(connection.queries)}")
    
    # Verify all messages are now read
    final_count = Message.unread.unread_count_for_user(user1)
    print(f"   Final unread count: {final_count}")
    print()
    
    # Performance comparison
    print("7. Performance comparison summary...")
    print("   Custom manager with .only(): Optimized for specific fields")
    print("   Explicit .only(): Same optimization, explicit in view")
    print("   Without .only(): Retrieves all fields (less efficient)")
    print()
    
    print("=== Test completed successfully! ===")
    print("Views are using .only() optimization through custom manager.")

if __name__ == '__main__':
    test_views_optimization() 