from rest_framework import pagination


class MyPaginator(pagination.PageNumberPagination):
    page_size = 2
    page_query_param = "page"
    page_size_query_param = "size"
    max_page_size = 5
