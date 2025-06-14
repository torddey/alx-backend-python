#!/usr/bin/env python3
"""
Test script to demonstrate logging various items to request.log
"""
import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from chats.middleware import RequestLoggingMiddleware

def test_logging():
    """Test various logging scenarios"""
    
    # Create an instance of the middleware
    middleware = RequestLoggingMiddleware(None)
    
    print("Testing logging functionality...")
    
    # Test authentication logging
    middleware.log_auth_attempt("john_doe", True, "192.168.1.100")
    middleware.log_auth_attempt("jane_smith", False, "192.168.1.101")
    
    # Test error logging
    middleware.log_error("ValidationError", "Invalid email format", "john_doe", "192.168.1.100")
    middleware.log_error("PermissionDenied", "User not authorized for this action", "anonymous", "192.168.1.102")
    
    # Test custom event logging
    middleware.log_custom_event("USER_REGISTRATION", "New user registered successfully", "john_doe")
    middleware.log_custom_event("MESSAGE_SENT", "Message sent to conversation_id: 123e4567-e89b-12d3-a456-426614174000", "jane_smith")
    middleware.log_custom_event("CONVERSATION_CREATED", "New conversation created with 3 participants", "admin")
    
    print("Logging test completed! Check requests.Log file for results.")

if __name__ == "__main__":
    test_logging() 