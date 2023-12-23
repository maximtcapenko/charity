from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Task


@login_required
def get_list(request):
    return render(request, 'tasks_list.html', {
        'tasks': Task.objects.all()
    })


@login_required
def get_details(request, id):
    task = get_object_or_404(Task, pk=id)
    paginator = Paginator(task.comments.filter(\
        reply_id__isnull=True).order_by('date_created'), per_page=10)

    return render(request, 'task_details.html', {
        'task': task,
        'comments_page': paginator.get_page(request.GET.get('page'))
    })
