from django.shortcuts import get_object_or_404

from .models import Task


def get_task_or_404(request, task_id):
    return get_object_or_404(Task.objects.filter(
        project__fund=request.user.fund),
        pk=task_id)
