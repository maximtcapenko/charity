from django.shortcuts import get_object_or_404

from commons.exceptions import ApplicationError

from .messages import Warnings
from .models import Project
from .requirements import user_should_be_project_author_or_leader


def get_project_or_404(request, project_id):
    return get_object_or_404(
        Project.objects.filter(
            fund__id=request.user.volunteer_profile.fund_id),
        pk=project_id)


def validate_pre_requirements(request, instance, return_url):
    if not user_should_be_project_author_or_leader(request.user, instance):
        raise ApplicationError(
            Warnings.CURRENT_USER_IS_NOT_PERMITTED, return_url)
