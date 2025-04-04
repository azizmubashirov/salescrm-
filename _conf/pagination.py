from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageSizePagination(PageNumberPagination):
    page_size_query_param = "size"
    page_size = 10
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(
            {"next": self.get_next_link(),
             "previous": self.get_previous_link(),

             "page_size": self.get_page_size(self.request),
             "current_page": self.page.number,
             "total_pages": self.page.paginator.num_pages,
             "page_items": len(self.page),
             "total": self.page.paginator.count,
             "results": data,
             }
        )
