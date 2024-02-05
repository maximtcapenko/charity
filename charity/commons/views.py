from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from .functional import user_should_be_volunteer


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def view_notification_details(request, id):
    notification = get_object_or_404(request.user.notifications.all(), pk=id)
    notification.is_viewed = True
    notification.save()

    return redirect(notification.url)
