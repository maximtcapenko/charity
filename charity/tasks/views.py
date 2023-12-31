from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer
from projects.models import Project
from .forms import CreateTaskForm, UpdateTaskForm
from .models import Task


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    return_url = reverse('projects:get_details', args=[
                         request.GET.get('project_id')])
    title = 'Add task'

    if request.method == 'POST':
        form = CreateTaskForm(request.POST)

        if form.is_valid():
            task = form.save()
            return redirect(reverse('projects:get_details', args=[task.project_id]))
        else:
            return render(request, 'generic_createform.html', {
                'title': title,
                'return_url': return_url,
                'form': form
            })
    elif request.method == 'GET':
        project = get_object_or_404(Project.objects.filter(
            fund_id=request.user.volunteer_profile.fund_id
        ), pk=request.GET.get('project_id'))

        return render(request, 'generic_createform.html', {
            'title': title,
            'return_url': return_url,
            'form': CreateTaskForm(initial={
                'project': project
            })
        })
    else:
        return HttpResponseNotAllowed([request.method])


@login_required
@user_passes_test(user_should_be_volunteer)
def update(request, id):
    return_url = reverse('tasks:get_details', args=[id])
    title = 'Update task'
    task = get_object_or_404(Task, pk=id)

    if request.method == 'POST':
        form = UpdateTaskForm(request.POST, initial={
            'project': task.project,
        }, instance=task)

        if form.is_valid():
            task = form.save()
            return redirect(return_url)
        else:
            return render(request, 'generic_createform.html', {
                'title': title,
                'return_url': return_url,
                'form': form
            })
    elif request.method == 'GET':
        return render(request, 'generic_createform.html', {
            'title': title,
            'return_url': return_url,
            'form': UpdateTaskForm(initial={
                'project': task.project,
            }, instance=task)
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
    tab = request.GET.get('tab', 'state_history')

    paginator = None
    if tab == 'comments':
        paginator = Paginator(task.comments.filter(
            reply_id__isnull=True).order_by('date_created'), per_page=DEFAULT_PAGE_SIZE)
    elif tab == 'files':
        paginator = Paginator(task.attachments.order_by(
            '-date_created'), per_page=DEFAULT_PAGE_SIZE)
    elif tab == 'state_history':
        state = task.state
        states = []

        while state is not None:
            states.append(state)
            state = state.prev_state

        paginator = Paginator(states, per_page=DEFAULT_PAGE_SIZE)

    return render(request, 'task_details.html', {
        'selected_tab': tab,
        'task': task,
        'page': paginator.get_page(request.GET.get('page'))
    })
