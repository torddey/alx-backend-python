import logging
import time
import json
from datetime import datetime
from django.http import HttpResponseForbidden


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

        if not (9 <= current_hour < 10):
            return HttpResponseForbidden("Access to the messaging app is restricted outside 9 AM to 6 OM")
        
        response = self.get_response(request)
        return response 

