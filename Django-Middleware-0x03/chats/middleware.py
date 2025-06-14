import logging
import time
import json
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden, JsonResponse
from collections import defaultdict


logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('requests.Log'),
    ]
)

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timing
        start_time = time.time()
        
        # Get user information
        user = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous"
        
        # Get request details
        method = request.method
        path = request.path
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Log request start
        logger.info(f"[REQUEST START] {datetime.now()} - User: {user} - IP: {ip_address} - Method: {method} - Path: {path} - User-Agent: {user_agent}")

        response = self.get_response(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log response details
        status_code = response.status_code
        logger.info(f"[REQUEST END] {datetime.now()} - User: {user} - Method: {method} - Path: {path} - Status: {status_code} - Response Time: {response_time:.3f}s")
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def log_auth_attempt(username, success, ip_address):
        """Log authentication attempts"""
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"[AUTH] {datetime.now()} - Username: {username} - Status: {status} - IP: {ip_address}")
    
    @staticmethod
    def log_error(error_type, message, user="Anonymous", ip_address="Unknown"):
        """Log errors"""
        logger.error(f"[ERROR] {datetime.now()} - Type: {error_type} - User: {user} - IP: {ip_address} - Message: {message}")
    
    @staticmethod
    def log_custom_event(event_type, details, user="Anonymous"):
        """Log custom events"""
        logger.info(f"[EVENT] {datetime.now()} - Type: {event_type} - User: {user} - Details: {details}")

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour 

        if not (9 <= current_hour < 18):  # 9 AM to 6 PM
            return HttpResponseForbidden("Access to the messaging app is restricted outside 9 AM to 6 PM")
        
        response = self.get_response(request)
        return response 


class OffensiveLanguageMiddleware:
    """
    Middleware to limit the number of chat messages a user can send within a time window.
    Limits: 5 messages per minute per IP address.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Store IP addresses and their message counts with timestamps
        self.ip_message_counts = defaultdict(list)
        self.max_messages = 5  # Maximum messages allowed
        self.time_window = 60  # Time window in seconds (1 minute)
    
    def __call__(self, request):
        # Only apply rate limiting to POST requests (message sending)
        if request.method == 'POST':
            ip_address = self.get_client_ip(request)
            
            # Check if this is a message-related endpoint
            if self.is_message_endpoint(request.path):
                if self.is_rate_limited(ip_address):
                    # Log the rate limit violation
                    RequestLoggingMiddleware.log_error(
                        "RateLimitExceeded", 
                        f"IP {ip_address} exceeded {self.max_messages} messages per minute", 
                        "Anonymous", 
                        ip_address
                    )
                    
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'You can only send {self.max_messages} messages per minute. Please wait before sending more messages.',
                        'retry_after': self.get_retry_after(ip_address)
                    }, status=429)  # 429 Too Many Requests
                
                # If not rate limited, record this message
                self.record_message(ip_address)
                
                # Log successful message
                RequestLoggingMiddleware.log_custom_event(
                    "MESSAGE_SENT", 
                    f"Message sent from IP {ip_address}", 
                    "Anonymous"
                )
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_message_endpoint(self, path):
        """Check if the request path is for sending messages"""
        # Add your message endpoints here
        message_endpoints = [
            '/api/messages/',
            '/api/conversations/',
            '/chats/messages/',
            '/messages/'
        ]
        return any(path.startswith(endpoint) for endpoint in message_endpoints)
    
    def is_rate_limited(self, ip_address):
        """Check if the IP address has exceeded the rate limit"""
        current_time = time.time()
        
        # Clean old entries (older than time_window)
        self.ip_message_counts[ip_address] = [
            timestamp for timestamp in self.ip_message_counts[ip_address]
            if current_time - timestamp < self.time_window
        ]
        
        # Check if current count exceeds limit
        return len(self.ip_message_counts[ip_address]) >= self.max_messages
    
    def record_message(self, ip_address):
        """Record a message for the given IP address"""
        current_time = time.time()
        self.ip_message_counts[ip_address].append(current_time)
    
    def get_retry_after(self, ip_address):
        """Calculate how many seconds to wait before retrying"""
        if not self.ip_message_counts[ip_address]:
            return 0
        
        # Get the oldest message timestamp
        oldest_message = min(self.ip_message_counts[ip_address])
        current_time = time.time()
        
        # Calculate when the oldest message will expire
        return max(0, int(self.time_window - (current_time - oldest_message)))

