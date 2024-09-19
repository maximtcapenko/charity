import msal
import time

from django.urls import reverse

from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.http import require_GET

from .functional import user_should_be_volunteer


@user_passes_test(user_should_be_volunteer)
@login_required
@require_GET
def view_notification_details(request, id):
    notification = get_object_or_404(request.user.notifications.all(), pk=id)
    notification.is_viewed = True
    notification.save()

    return redirect(notification.url)


def azure_ad_login(request):
    msal_app = msal.ConfidentialClientApplication(
        settings.AZURE_AD_CLIENT_ID,
        authority=settings.AZURE_AD_AUTHORITY,
        client_credential=settings.AZURE_AD_CLIENT_SECRET
    )
    auth_url = msal_app.get_authorization_request_url(
        settings.AZURE_AD_SCOPE,
        redirect_uri=settings.AZURE_AD_REDIRECT_URI
    )
    return redirect(auth_url)


def azure_ad_callback(request):
    code = request.GET.get('code')
    if not code:
        return HttpResponse('No code provided', status=400)

    msal_app = msal.ConfidentialClientApplication(
        settings.AZURE_AD_CLIENT_ID,
        authority=settings.AZURE_AD_AUTHORITY,
        client_credential=settings.AZURE_AD_CLIENT_SECRET
    )
    accounts = msal_app.get_accounts()
    if accounts:
        result = msal_app.acquire_token_silent_with_error(
            scopes=settings.AZURE_AD_SCOPE, account=accounts[0])
    else:
        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=settings.AZURE_AD_SCOPE,
            redirect_uri=settings.AZURE_AD_REDIRECT_URI)

    if 'access_token' in result:
        user_info = result['id_token_claims']
        username = user_info.get('preferred_username') or user_info.get('email')
      
        user = User.objects.filter(email=username).first()
        if not user:
            user = User.objects.create(username=username, email=username)
            user.save()

        if not user_should_be_volunteer(user):
            return redirect('user_is_not_approved')

        login(request, user)
        request.session['login_hint'] = user_info['login_hint']
        request.session['refresh_token'] = result['refresh_token']
        request.session['expires_at'] = int(time.time()) + result['expires_in']

        return redirect(reverse('funds:get_current_details'))
    else:
        return HttpResponse('Authentication failed', status=400)


@login_required
def ad_logout(request):
    msal_app = msal.ConfidentialClientApplication(
        settings.AZURE_AD_CLIENT_ID,
        authority=settings.AZURE_AD_AUTHORITY,
        client_credential=settings.AZURE_AD_CLIENT_SECRET
    )
    accounts = msal_app.get_accounts()
    if accounts:
        msal_app.remove_account(accounts[0])
    login_hint = request.session['login_hint']
    logout(request)
    return redirect(f'https://login.microsoftonline.com/common/oauth2/v2.0/logout?logout_hint={login_hint}&post_logout_redirect_uri={request.META.get("HTTP_REFERER")}')


def user_is_not_approved(request):
    return render(request, 'wait_for_approve.html')