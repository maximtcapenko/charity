from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, render_generic_form
from funds.models import VolunteerProfile
from projects.models import Project

from .forms import CreateTaskForm, UpdateTaskForm, \
    CreateCommentForm, ActivateTaskStateForm, ApproveTaskStateForm, \
    TaskCreateAttachmentForm
from .models import Task


def _get_task_or_404(request, task_id):
    return get_object_or_404(Task.objects.filter(
        project__fund__id=request.user.volunteer_profile.fund_id),
        pk=task_id)


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
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
            },
            'post_form_initial': {
                'project': project,
                'user': request.user
            }
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
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


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
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


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def add_comment(request, id):
    return_url = f"{reverse('tasks:get_details', args=[id])}?tab=comments"
    task = _get_task_or_404(request, id)

    return render_generic_form(
        request=request, form_class=CreateCommentForm, context={
            'title': 'Add new comment',
            'return_url': return_url,
            'get_form_initial': {
                'author': request.user,
                'task': task
            },
            'post_form_initial': {
                'author': request.user,
                'task': task
            }
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def reply_to_comment(request, task_id, id):
    task = _get_task_or_404(request, task_id)
    comment = get_object_or_404(task.comments, pk=id)
    return_url = f"{reverse('tasks:get_comment_details', args=[task_id, id])}"
    initial = {
        'author': request.user,
        'reply': comment,
        'task': task
    }
    return render_generic_form(
        request=request, form_class=CreateCommentForm, context={
            'title': 'Reply',
            'return_url': return_url,
            'get_form_initial': initial,
            'post_form_initial': initial
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
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


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def attach_file(request, id):
    task = _get_task_or_404(request, id)
    return render_generic_form(
        request=request,
        form_class=TaskCreateAttachmentForm,
        context={
            'return_url': '%s?%s' % (
                reverse('tasks:get_details', args=[id]), 'tab=files'),
            'title': 'Upload file',
            'post_form_initial': {
                'user': request.user,
                'task': task,
                'fund': request.user.volunteer_profile.fund
            }
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_details(request, id):
    default_tab = 'states'
    tabs = {
        'states': lambda task: task.states.select_related('author'),
        'comments': lambda task: task.comments.filter(
            reply_id__isnull=True).annotate(
                replies_count=models.Count('replies')).order_by('date_created')
        .values('id', 'author__id', 'author__username', 'date_created', 'notes', 'replies_count'),
        'files': lambda task:  task.attachments.all()
    }

    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab
    task = _get_task_or_404(request, id)

    if tab == 'comments':
        authors_queryset = VolunteerProfile.objects.filter(
            user_id__in=User.objects.filter(comments__task=task)).all()
        authors = {authors_queryset[i].user_id: authors_queryset[i]
                   for i in range(0, len(authors_queryset), 1)}
    else:
        authors = None

    queryset = tabs.get(tab)(task)
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    return render(request, 'task_details.html', {
        'tabs': tabs.keys(),
        'items_count': paginator.count,
        'authors': authors,
        'selected_tab': tab,
        'task': task,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_comment_details(request, task_id, id):
    task = _get_task_or_404(request, task_id)
    comment = get_object_or_404(task.comments, pk=id)

    paginator = Paginator(
        comment.replies.select_related('author', 'author__volunteer_profile')
        .order_by('date_created'),
        per_page=DEFAULT_PAGE_SIZE)

    return render(request, 'task_comment_details.html', {
        'comment': comment,
        'task': task,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_state_details(request, task_id, id):
    task = _get_task_or_404(request, task_id)
    state = get_object_or_404(task.states, pk=id)

    paginator = Paginator(state.approvements.all(),
                          per_page=DEFAULT_PAGE_SIZE)

    return render(request, 'task_state_details.html', {
        'task': task,
        'state': state,
        'page': paginator.get_page(request.GET.get('page'))
    })
