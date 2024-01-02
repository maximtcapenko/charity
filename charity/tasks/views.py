import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer
from projects.models import Project
from .forms import CreateTaskForm, UpdateTaskForm, CreateCommentForm
from .models import Task, Comment, TaskState


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
def add_comment(request, id):
    return_url = '%s?%s' % (
        reverse('tasks:get_details', args=[id]), 'tab=comments')
    title = 'Add new comment'
    task = get_object_or_404(Task, pk=id)

    if request.method == 'POST':
        form = CreateCommentForm(request.POST, initial={
            'author': request.user,
            'task': task
        })

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
            'form': CreateCommentForm(initial={
                'author': request.user
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
    tab = request.GET.get('tab', 'state_history')

    paginator = None
    if tab == 'comments':
        paginator = Paginator(task.comments.filter(
            reply_id__isnull=True)
            .annotate(replies_count=models.Count('replies'))
            .order_by('date_created')
            .values('id', 'author__username', 'date_created', 'notes', 'replies_count'),
            per_page=DEFAULT_PAGE_SIZE)
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


@login_required
@user_passes_test(user_should_be_volunteer)
def get_comment_details(request, id):
    comment = get_object_or_404(Comment, pk=id)

    replies_page = Paginator(
        comment.replies.select_related('author')
        .order_by('date_created'),
        per_page=DEFAULT_PAGE_SIZE)

    return render(request, 'task_comment_details.html', {
        'comment': comment,
        'replies_page': replies_page
    })
