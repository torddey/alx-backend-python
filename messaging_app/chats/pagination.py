from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for API responses.
    """
    page_size = 20
    page_size_query_param = 'page_size'  
    max_page_size = 100  