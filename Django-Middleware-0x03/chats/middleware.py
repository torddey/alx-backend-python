import logging
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
        user = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous"

        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        response = self.get_response(request)
        return response
    

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour 

        if not (9 <= current_hour < 10):
            return HttpResponseForbidden("Access to the messaging app is restricted outside 9 AM to 6 OM")
        
        response = self.get_response(request)
        return response 

