from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer
from projects.models import Project
from .forms import CreateTaskForm
from .models import Task


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    if request.method == 'POST':
        form = CreateTaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=True)
            return redirect(reverse('projects:get_details', args=[task.project_id]))
        else:
            return render(request, 'generic_createform.html', {
                'title': 'Add task',
                'return_url': reverse('projects:get_details', args=[request.GET.get('project_id')]),
                'form': form
            })
    elif request.method == 'GET':
        project = get_object_or_404(Project.objects.filter(
            fund_id=request.user.volunteer_profile.fund_id
        ), pk=request.GET.get('project_id'))

        return render(request, 'generic_createform.html', {
            'title': 'Add task',
            'return_url': reverse('projects:get_details', args=[request.GET.get('project_id')]),
            'form': CreateTaskForm(initial={
                'project': project
            })
        })
    else:
        return HttpResponseNotAllowed([request.method])


@login_required
@user_passes_test(user_should_be_volunteer)
def get_list(request):
    return render(request, 'tasks_list.html', {
        'tasks': Task.objects.all()
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    task = get_object_or_404(Task, pk=id)
    paginator = Paginator(task.comments.filter(
        reply_id__isnull=True).order_by('date_created'), per_page=DEFAULT_PAGE_SIZE)

    return render(request, 'task_details.html', {
        'task': task,
        'comments_page': paginator.get_page(request.GET.get('page'))
    })
