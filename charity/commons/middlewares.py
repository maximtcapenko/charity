from django.shortcuts import render

from .exceptions import ApplicationError


class BadRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, ApplicationError):
            return render(request, '400.html', {
                'error_message': exception.error_message,
                'return_url': exception.return_url
            })
        return None
