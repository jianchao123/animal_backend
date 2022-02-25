# coding:utf-8
from rest_framework.pagination import PageNumberPagination


class LargeResultsSetPagination(PageNumberPagination):
    # 每页显示多少个
    page_size = 200
    # 默认每页显示3个，可以通过传入pager1/?page=2&size=4,改变默认每页显示的个数
    page_size_query_param = "limit"
    # 最大页数不超过10
    max_page_size = 200
    # 获取页码数的
    page_query_param = "page"


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000