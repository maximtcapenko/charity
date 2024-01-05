from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, render_generic_form
from projects.models import Project

from .forms import CreateTaskForm, UpdateTaskForm, \
    CreateCommentForm, ActivateTaskStateForm, ApproveTaskStateForm
from .models import Task, Comment, TaskState


def _get_task_or_404(request, task_id):
    return get_object_or_404(Task.objects.filter(
        project__fund__id=request.user.volunteer_profile.fund_id),
        pk=task_id)


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    project_id = request.GET.get('project_id')
    project = get_object_or_404(Project.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id
    ), pk=project_id)

    return render_generic_form(
        request=request, form_class=CreateTaskForm, context={
            'title': 'Add task',
            'return_url': reverse('projects:get_details', args=[project_id]),
            'get_form_initial': {
                'project': project
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def edit_details(request, id):
    task = _get_task_or_404(request, id)
    return render_generic_form(
        request=request, form_class=UpdateTaskForm, context={
            'return_url': reverse('tasks:get_details', args=[id]),
            'title': 'Update task',
            'instance': task,
            'get_form_initial': {
                'project': task.project
            },
            'post_form_initial': {
                'project': task.project
            }
        }
    )


@login_required
@user_passes_test(user_should_be_volunteer)
def move_to_next_state(request, id):
    task = _get_task_or_404(request, id)
    return render_generic_form(
        request=request, form_class=ActivateTaskStateForm, context={
            'return_url': reverse('tasks:get_details', args=[id]),
            'title': 'Move task to next state',
            'get_form_initial': {
                'task': task
            },
            'post_form_initial': {
                'task': task,
                'user': request.user
            }
        }
    )


@login_required
@user_passes_test(user_should_be_volunteer)
def add_comment(request, id):
    return_url = '%s?%s' % (
        reverse('tasks:get_details', args=[id]), 'tab=comments')
    task = _get_task_or_404(request, id)

    return render_generic_form(
        request=request, form_class=CreateCommentForm, context={
            'title': 'Add new comment',
            'return_url': return_url,
            'get_form_initial': {
                'author': request.user
            },
            'post_form_initial': {
                'author': request.user,
                'task': task
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def approve_task_state(request, task_id, id):
    task = _get_task_or_404(request, task_id)
    state = get_object_or_404(task.states, pk=id)

    return render_generic_form(
        request=request,
        form_class=ApproveTaskStateForm,
        context={
            'return_url': '%s?%s' % (
                reverse('tasks:get_details', args=[task_id]), 'tab=states'),
            'title': 'Approve task',
            'post_form_initial': {
                'user': request.user,
                'state': state,
                'fund': request.user.volunteer_profile.fund
            }
        }
    )


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    default_tab = 'states'
    tabs = {
        'states': lambda task: Paginator(task.states
                                         .select_related('author')
                                         .order_by('-date_created'),
                                         per_page=DEFAULT_PAGE_SIZE),
        'comments': lambda task: Paginator(task.comments.filter(
            reply_id__isnull=True)
            .annotate(replies_count=models.Count('replies'))
            .order_by('date_created')
            .values('id', 'author__username', 'date_created', 'notes', 'replies_count'),
            per_page=DEFAULT_PAGE_SIZE),
        'files': lambda task: Paginator(task.attachments.order_by(
            '-date_created'), per_page=DEFAULT_PAGE_SIZE)
    }

    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab
    task = _get_task_or_404(request, id)

    paginator = tabs.get(tab)(task)

    return render(request, 'task_details.html', {
        'tabs': tabs.keys(),
        'selected_tab': tab,
        'task': task,
        'page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_comment_details(request, id):
    comment = get_object_or_404(Comment, pk=id)

    paginator = Paginator(
        comment.replies.select_related('author')
        .order_by('date_created'),
        per_page=DEFAULT_PAGE_SIZE)

    return render(request, 'task_comment_details.html', {
        'comment': comment,
        'page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_state_details(request, task_id, id):
    task = _get_task_or_404(request, task_id)
    state = task.states.get(pk=id)

    paginator = Paginator(state.approvements.order_by('-date_created'),
                          per_page=DEFAULT_PAGE_SIZE)

    return render(request, 'task_state_details.html', {
        'task': task,
        'state': state,
        'page': paginator.get_page(request.GET.get('page'))
    })
