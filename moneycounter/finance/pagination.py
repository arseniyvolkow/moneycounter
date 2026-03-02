from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class for API responses.
    Defaults to 10 items per page, configurable via the 'page_size' query parameter up to 100.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100