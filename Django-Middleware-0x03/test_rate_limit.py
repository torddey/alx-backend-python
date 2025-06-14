#!/usr/bin/env python3
"""
Test script to demonstrate the rate limiting functionality
"""
import os
import sys
import django
import time
import requests
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from chats.middleware import OffensiveLanguageMiddleware

def test_rate_limiting():
    """Test the rate limiting functionality"""
    
    print("Testing Rate Limiting Middleware...")
    print("=" * 50)
    
    # Create an instance of the middleware
    middleware = OffensiveLanguageMiddleware(None)
    
    # Test IP address
    test_ip = "192.168.1.100"
    
    print(f"Testing with IP: {test_ip}")
    print(f"Limit: {middleware.max_messages} messages per {middleware.time_window} seconds")
    print()
    
    # Simulate sending messages
    for i in range(7):  # Try to send 7 messages (exceeds the 5 message limit)
        print(f"Attempt {i + 1}: Sending message...")
        
        # Check if rate limited
        if middleware.is_rate_limited(test_ip):
            retry_after = middleware.get_retry_after(test_ip)
            print(f"❌ RATE LIMITED! Must wait {retry_after} seconds")
            print(f"   Current message count: {len(middleware.ip_message_counts[test_ip])}")
        else:
            # Record the message
            middleware.record_message(test_ip)
            print(f"✅ Message sent successfully")
            print(f"   Current message count: {len(middleware.ip_message_counts[test_ip])}")
        
        print()
        time.sleep(1)  # Wait 1 second between attempts
    
    print("Rate limiting test completed!")
    print("Check the requests.Log file for detailed logs.")

def test_multiple_ips():
    """Test rate limiting with multiple IP addresses"""
    
    print("\nTesting Multiple IP Addresses...")
    print("=" * 50)
    
    middleware = OffensiveLanguageMiddleware(None)
    
    ips = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
    
    for ip in ips:
        print(f"\nTesting IP: {ip}")
        
        # Send 3 messages for each IP
        for i in range(3):
            if middleware.is_rate_limited(ip):
                print(f"❌ Rate limited for IP {ip}")
                break
            else:
                middleware.record_message(ip)
                print(f"✅ Message {i + 1} sent from {ip}")
        
        print(f"Final count for {ip}: {len(middleware.ip_message_counts[ip])} messages")

if __name__ == "__main__":
    test_rate_limiting()
    test_multiple_ips() 