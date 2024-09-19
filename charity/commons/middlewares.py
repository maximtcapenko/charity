import time
from django.urls import reverse
import msal

from django.conf import settings
from django.shortcuts import redirect
from django.utils import http
from django.utils.translation import gettext_lazy as _

from urllib.parse import urlparse

from .exceptions import ApplicationError


class BadRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, ApplicationError):
            message = http.urlsafe_base64_encode(
                _(exception.error_message).encode('utf-8'))
            parse_result = urlparse(exception.return_url)
            if parse_result.query:
                url = f'{exception.return_url}&message={message}'
            else:
                url = f'{exception.return_url}?message={message}'
            return redirect(url)

        return None


class TokenRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        refresh_token = request.session.get('refresh_token')
        expires_at = request.session.get('expires_at')

        if refresh_token and expires_at:
            current_time = int(time.time())

            if current_time > expires_at - 300:
                msal_app = msal.ConfidentialClientApplication(
                    settings.AZURE_AD_CLIENT_ID,
                    authority=settings.AZURE_AD_AUTHORITY,
                    client_credential=settings.AZURE_AD_CLIENT_SECRET
                )
                result = msal_app.acquire_token_by_refresh_token(
                    refresh_token, scopes=settings.AZURE_AD_SCOPE)

                if 'access_token' in result:
                    request.session['access_token'] = result['access_token']
                    request.session['refresh_token'] = result.get(
                        'refresh_token', refresh_token)
                    request.session['expires_at'] = current_time + \
                        result['expires_in']

                else:
                    return redirect(reverse('funds:get_current_details'))

        response = self.get_response(request)
        return response
