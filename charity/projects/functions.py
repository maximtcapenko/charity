from django.shortcuts import get_object_or_404

from .models import Project


def get_project_or_404(request, project_id):
    return get_object_or_404(
        Project.objects.filter(
            fund__id=request.user.volunteer_profile.fund_id),
        pk=project_id)
