from django.shortcuts import redirect
from django.utils import http

from .exceptions import ApplicationError


class BadRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, ApplicationError):
            message = http.urlsafe_base64_encode(
                exception.error_message.encode('utf-8'))
            parse_result = http.urlparse(exception.return_url)
            if parse_result.query:
                url = f'{exception.return_url}&message={message}'
            else:
                url = f'{exception.return_url}?message={message}'
            return redirect(url)

        return None
