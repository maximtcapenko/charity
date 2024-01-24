from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Exists, Q, OuterRef
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.exceptions import ApplicationError
from commons.functions import render_generic_form, user_should_be_volunteer
from funds.models import Approvement
from tasks.models import Task, TaskState

from .forms import CreateProjectForm, AddWardToProjectForm, \
    AddProcessToProjectForm, UpdateProjectForm, AddProjectReviewerForm
from .functions import get_project_or_404
from .models import Project
from .renderers import TasksBoardRenderer


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_ward_to_project(request, id):
    project = get_project_or_404(request=request, project_id=id)
    return_url = reverse('projects:get_details', args=[
        project.id]) + '?tab=wards'

    return render_generic_form(
        request=request, form_class=AddWardToProjectForm,
        context={
            'return_url': return_url,
            'title': 'Include ward to project',
            'initial': {
                'project': project
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_process_to_project(request, id):
    project = get_project_or_404(request=request, project_id=id)
    return_url = reverse('projects:get_details', args=[
        project.id]) + '?tab=processes'

    return render_generic_form(
        request=request, form_class=AddProcessToProjectForm,
        context={
            'return_url': return_url,
            'title': 'Include process to project',
            'initial': {
                'project': project
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_details(request, id):
    project = get_project_or_404(request=request, project_id=id)
    return render_generic_form(
        request=request, form_class=UpdateProjectForm, context={
            'return_url': reverse('projects:get_details', args=[project.id]),
            'title': 'Update project',
            'initial': {
                'fund': request.user.volunteer_profile.fund
            },
            'instance': project
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def close(request, id):
    project = get_object_or_404(Project, pk=id)
    return HttpResponseNotAllowed([request.method])


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def create(request):
    return render_generic_form(
        request=request, form_class=CreateProjectForm,
        context={
            'return_url': '%s?%s' % (reverse('funds:get_current_details'), 'tab=projects'),
            'title': 'Add project',
            'initial': {
                'fund': request.user.volunteer_profile.fund
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_project_reviewer(request, id):
    return render_generic_form(
        request=request, form_class=AddProjectReviewerForm, context={
            'return_url': f'{reverse("projects:get_details", args=[id])}?tab=reviewers',
            'title': 'Add project reviewer',
            'initial': {
                'project': get_project_or_404(request, id)
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_project_process(request, id, process_id):
    project = get_project_or_404(request, id)
    return_url = f'{reverse("projects:get_details", args=[id])}?tab=processes'

    if project.tasks.filter(process__id=process_id).exists():
        raise ApplicationError(
            'Process can not be removed from project because it is used by tasks', return_url)

    process = get_object_or_404(project.processes, pk=process_id)
    project.processes.remove(process)

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_project_task(request, id, task_id):
    project = get_project_or_404(request, id)
    return_url = f'{reverse("projects:get_details", args=[id])}?tab=tasks'

    if project.tasks.filter(Q(id=task_id) &
                            Q(Q(expense__id__isnull=False) |
                              Q(state__id__isnull=False))).exists():
        raise ApplicationError(
            'Task can not be removed from project because task is started or has expense', return_url)

    task = get_object_or_404(project.tasks, pk=task_id)
    task.delete()

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_project_ward(request, id, ward_id):
    project = get_project_or_404(request, id)
    return_url = f'{reverse("projects:get_details", args=[id])}?tab=wards'

    if project.wards.filter(
            Q(id=ward_id) &
            Exists(Task.objects.filter(project=project, ward=OuterRef('pk')))).exists():
        raise ApplicationError(
            'Ward can not be removed from project because of usage in tasks', return_url)

    ward = get_object_or_404(project.wards, pk=ward_id)
    project.wards.remove(ward)

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_project_reviewer(request, id, reviewer_id):
    project = get_project_or_404(request, id)
    return_url = f'{reverse("projects:get_details", args=[id])}?tab=reviewers'

    if project.tasks.filter(Q(state__approvement__author__id=reviewer_id) |
                            Q(reviewer__id=reviewer_id)).exists():
        raise ApplicationError(
            'Reviewer can not be removed from project because of reviewed tasks in project', return_url)

    if project.reviewers.count() == 1:
        """redirect to error page with return url"""
        raise ApplicationError(
            'Project must have at least one reviewer', return_url)

    reviewer = get_object_or_404(project.reviewers, pk=reviewer_id)
    project.reviewers.remove(reviewer)

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_list(request):
    paginator = Paginator(Project.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id)
        .select_related(
            'leader', 'leader__volunteer_profile'), DEFAULT_PAGE_SIZE)
    return render(request, 'projects_list.html', {
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_details(request, id):
    default_tab = 'tasks'
    tabs = {
        'tasks': lambda project: project.tasks.
        select_related(
            'assignee', 'expense',
            'expense__approvement',
            'assignee__volunteer_profile')
        .order_by('order_position'),
        'processes': lambda project: project.processes.all(),
        'wards': lambda project: project.wards.all(),
        'reviewers': lambda project: project.reviewers.select_related('volunteer_profile')

    }

    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    project = get_object_or_404(Project.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)

    queryset = tabs.get(tab)(project)
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    page = paginator.get_page(request.GET.get('page'))
    tasks_renderer = None
    if tab == 'tasks':
        tasks_renderer = TasksBoardRenderer(project, page, request)

    return render(request, 'project_details.html', {
        'title': 'Project',
        'tabs': tabs.keys(),
        'items_count': paginator.count,
        'project': project,
        'selected_tab': tab,
        'tasks_renderer': tasks_renderer,
        'page': page
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_reviewer_details(request, id, reviewer_id):
    project = get_object_or_404(Project.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)

    reviewer = get_object_or_404(project.reviewers, pk=reviewer_id)

    queryset = TaskState.objects.filter(
        Q(task__project=project) &
        Exists(Approvement.objects.filter(approved_task_states=OuterRef('pk'), author=reviewer))) \
        .prefetch_related('approvements') \
        .prefetch_related('state_tasks') \
        .select_related('state')
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    return render(request, 'project_reviewer_details.html', {
        'project': project,
        'reviewer': reviewer,
        'page': paginator.get_page(request.GET.get('page'))
    })
