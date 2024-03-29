from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.exceptions import ApplicationError
from commons.functional import user_should_be_volunteer, render_generic_form
from processes.models import ProcessState
from projects.models import Project

from .querysets import get_available_task_process_states_queryset
from .forms import CreateTaskForm, UpdateTaskForm, \
    ActivateTaskStateForm, ApproveTaskStateForm, \
    TaskStateReviewRequestForm, CompleteTaskForm
from .functional import get_task_or_404
from .messages import Warnings
from .requirements import task_state_is_ready_for_review, \
    task_state_is_ready_for_review_request, task_is_ready_to_be_completed


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_task(request):
    project_id = request.GET.get('project_id')
    project = get_object_or_404(Project.objects.filter(
        fund=request.user.fund
    ), pk=project_id)

    return render_generic_form(
        request=request, form_class=CreateTaskForm, context={
            'title': 'Add task',
            'return_url': reverse('projects:get_details', args=[project_id]),
            'initial': {
                'project': project,
                'author': request.user
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_details(request, id):
    default_tab = 'process'
    tabs = [
        'process',
        'comments',
        'files'
    ]
    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    task = get_task_or_404(request, id)

    paginator = Paginator(ProcessState.objects.filter(
        process_id=task.process_id).all(), DEFAULT_PAGE_SIZE)

    return render(request, 'task_details.html', {
        'title': 'Task',
        'tabs': tabs,
        'model_name': task._meta.model_name,
        'items_count': paginator.count,
        'selected_tab': tab,
        'task': task,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_details(request, id):
    task = get_task_or_404(request, id)
    return render_generic_form(
        request=request, form_class=UpdateTaskForm, context={
            'return_url': reverse('tasks:get_details', args=[id]),
            'title': 'Update task',
            'instance': task,
            'initial': {
                'project': task.project,
                'author': request.user
            }
        }
    )


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def complete_task(request, id):
    task = get_task_or_404(request, id)
    return_url = reverse('tasks:get_details', args=[id])
    if not task_is_ready_to_be_completed(task, request.user):
        raise ApplicationError(
            Warnings.TASK_IS_NOT_READY_TO_BE_COMPLETED, return_url)
    return render_generic_form(
        request=request, form_class=CompleteTaskForm, context={
            'title': f'Complete task {task.name}',
            'return_url': return_url,
            'initial': {
                'task': task,
                'author': request.user,
                'fund': request.user.fund
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def start_next_state(request, id):
    task = get_task_or_404(request, id)
    process_state_id = request.GET.get('process_state_id')
    process_state = None

    if process_state_id:
        '''validate if this state exists in process and it is avaliable to be acrivated'''
        queryset = get_available_task_process_states_queryset(task)
        process_state = get_object_or_404(queryset, pk=process_state_id)

    return render_generic_form(
        request=request, form_class=ActivateTaskStateForm, context={
            'return_url': reverse('tasks:get_details', args=[id]),
            'title': 'Start next state',
            'initial': {
                'task': task,
                'author': request.user,
                'state': process_state
            }
        }
    )


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def approve_task_state(request, task_id, id):
    task = get_task_or_404(request, task_id)
    state = get_object_or_404(task.states, pk=id)
    return_url = reverse('tasks:get_state_details', args=[task_id, id])
    if not task_state_is_ready_for_review(state, request.user, task):
        raise ApplicationError(
            Warnings.TASK_STATE_IS_NOT_READY_FOR_REVIEW, return_url)

    return render_generic_form(
        request=request,
        form_class=ApproveTaskStateForm,
        context={
            'return_url': return_url,
            'title': 'Approve task',
            'initial': {
                'author': request.user,
                'state': state,
                'fund': request.user.fund,
                'task': task
            }
        }
    )


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def request_task_state_review(request, task_id, id):
    task = get_task_or_404(request, task_id)
    state = get_object_or_404(task.states, pk=id)

    if not task_state_is_ready_for_review_request(state, request.user, task):
        raise ApplicationError(Warnings.TASK_STATE_IS_NOT_READY_FOR_REVIEW)

    return render_generic_form(
        request=request,
        form_class=TaskStateReviewRequestForm,
        context={
            'return_url':
            reverse('tasks:get_state_details', args=[task_id, id]),
                'title': 'Request task state review',
                'initial': {
                    'author': request.user,
                    'state': state,
                    'fund': request.user.fund,
                    'task': task
            }
        }
    )


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_state_details(request, task_id, id):
    default_tab = 'comments'
    tabs = [
        'comments',
        'reviews',
        'files'
    ]
    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    task = get_task_or_404(request, task_id)
    state = get_object_or_404(task.states, pk=id)

    paginator = Paginator(state.approvements.all(),
                          per_page=DEFAULT_PAGE_SIZE)

    return render(request, 'task_state_details.html', {
        'title': 'Task step',
        'tabs': tabs,
        'model_name': state._meta.model_name,
        'items_count': paginator.count,
        'selected_tab': tab,
        'task': task,
        'state': state,
        'page': paginator.get_page(request.GET.get('page'))
    })
