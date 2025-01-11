from collections import OrderedDict
from furl import furl
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param, remove_query_param

class CorePageNumberPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size = 30
    page_size_query_param = "max_page"
    max_page_size = 1000

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        ssl_check = str(self.request.META.get('HTTP_ORIGIN')).split(':')[0]
        url_combine = str(url).split(':')
        if len(str(url).split(':')) == 2:
            url = ssl_check + ':' + url_combine[1]
            if page_number == 1:
                return remove_query_param(url, self.page_query_param)
            return replace_query_param(url, self.page_query_param, page_number)
        elif len(str(url).split(':')) == 3:
            url = ssl_check + ':' + url_combine[1] + ':' + url_combine[2]
            if page_number == 1:
                return remove_query_param(url, self.page_query_param)
            return replace_query_param(url, self.page_query_param, page_number)
        else:
            raise APIException({"detail": "Wrong API Url"})

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        ssl_check = furl(str(self.request.META.get('HTTP_ORIGIN'))).scheme
        url_combine = str(url).split(':')
        if url_combine[0] != ssl_check:
            url = ssl_check + ':' + url_combine[1:]
            return replace_query_param(url, self.page_query_param, page_number)
        else:
            raise APIException({"detail": "Wrong API Url"})

    def query_data_add(self) -> list:
        return []


    def get_paginated_response(self, data):
        response_data = [
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]
        response_data += self.query_data_add()
        return Response(OrderedDict(response_data))

