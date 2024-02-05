from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Exists, Q, OuterRef
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.exceptions import ApplicationError
from commons.functional import render_generic_form, user_should_be_volunteer, \
    wrap_dicts_page_to_objects_page, get_wrapped_page, get_page

from funds.models import Approvement
from processes.models import Process
from tasks.models import Task, TaskState
from wards.models import Ward

from .forms import CreateProjectForm, AddWardToProjectForm, \
    AddProcessToProjectForm, UpdateProjectForm, AddProjectReviewerForm
from .functional import get_project_or_404, validate_pre_requirements
from .querysets import get_project_processes_with_tasks_queryset, \
    get_project_wards_with_tasks_queryset, get_projects_with_tasks_queryset, \
    get_project_rewiewers_with_tasks_queryset
from .messages import Warnings
from .models import Project
from .requirements import process_should_not_be_used_by_any_tasks, \
    project_should_not_contain_any_tasks, reviewer_should_not_be_used_by_any_tasks, \
    ward_should_not_be_used_by_any_tasks


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_project(request):
    return render_generic_form(
        request=request, form_class=CreateProjectForm,
        context={
            'return_url': reverse('projects:get_list'),
            'title': 'Add project',
            'initial': {
                'author': request.user,
                'fund': request.user.fund
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_project(request, id):
    project = get_project_or_404(request, id)
    return_url = reverse('projects:get_list')

    validate_pre_requirements(request, project, return_url)

    if not project_should_not_contain_any_tasks(project):
        raise ApplicationError(Warnings.PROJECT_TASKS_EXIST, return_url)

    project.delete()

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_project_details(request, id):
    project = get_project_or_404(request=request, project_id=id)
    return_url = reverse('projects:get_details', args=[project.id])

    validate_pre_requirements(request, project, return_url)

    return render_generic_form(
        request=request, form_class=UpdateProjectForm, context={
            'return_url': return_url,
            'title': 'Update project',
            'initial': {
                'fund': request.user.fund
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
def add_project_process(request, id):
    project = get_project_or_404(request=request, project_id=id)
    return_url = reverse('projects:get_details', args=[
        project.id]) + '?tab=processes'

    validate_pre_requirements(request, project, return_url)

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
@require_http_methods(['POST'])
def remove_project_process(request, id, process_id):
    project = get_project_or_404(request, id)
    return_url = f'{reverse("projects:get_details", args=[id])}?tab=processes'

    validate_pre_requirements(request, project, return_url)

    process = get_object_or_404(project.processes, pk=process_id)

    if not process_should_not_be_used_by_any_tasks(process, project):
        raise ApplicationError(
            Warnings.PROJECT_PROCESS_TASKS_EXIST, return_url)

    project.processes.remove(process)

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_project_ward(request, id):
    project = get_project_or_404(request=request, project_id=id)
    return_url = reverse('projects:get_details', args=[
        project.id]) + '?tab=wards'

    validate_pre_requirements(request, project, return_url)

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
@require_http_methods(['POST'])
def remove_project_ward(request, id, ward_id):
    project = get_project_or_404(request, id)
    return_url = f'{reverse("projects:get_details", args=[id])}?tab=wards'

    validate_pre_requirements(request, project, return_url)

    ward = get_object_or_404(project.wards, pk=ward_id)

    if not ward_should_not_be_used_by_any_tasks(ward, project):
        raise ApplicationError(
            Warnings.ASSET_CANNOT_BE_REMOVED_TASKS_EXIST, return_url)

    project.wards.remove(ward)

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_project_reviewer(request, id):
    project = get_project_or_404(request, id)
    return_url = f'{reverse("projects:get_details", args=[id])}?tab=reviewers'

    validate_pre_requirements(request, project, return_url)

    return render_generic_form(
        request=request, form_class=AddProjectReviewerForm, context={
            'return_url': return_url,
            'title': 'Add project reviewer',
            'initial': {
                'project': project
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_project_reviewer(request, id, reviewer_id):
    project = get_project_or_404(request, id)
    return_url = f'{reverse("projects:get_details", args=[id])}?tab=reviewers'

    validate_pre_requirements(request, project, return_url)

    reviewer = get_object_or_404(project.reviewers, pk=reviewer_id)

    if not reviewer_should_not_be_used_by_any_tasks(reviewer, project):
        raise ApplicationError(
            Warnings.PROJECT_REVIEWER_TASKS_EXIST, return_url)

    if project.leader == reviewer:
        raise ApplicationError(
            Warnings.LEADER_CANNOT_BE_REMOVED_FROM_PROJECT_REVIEWERS, return_url)

    if project.reviewers.count() == 1:
        """redirect to error page with return url"""
        raise ApplicationError(
            Warnings.PROJECT_REVIEWER_MUST_EXISTS, return_url)

    project.reviewers.remove(reviewer)

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_project_task(request, id, task_id):
    project = get_project_or_404(request, id)
    return_url = f'{reverse("projects:get_details", args=[id])}?tab=tasks'

    validate_pre_requirements(request, project, return_url)

    if project.tasks.filter(Q(id=task_id) &
                            Q(Q(expense__id__isnull=False) |
                              Q(state__id__isnull=False))).exists():
        raise ApplicationError(
            Warnings.PROJECT_TASK_ISRUNNING, return_url)

    task = get_object_or_404(project.tasks, pk=task_id)
    task.delete()

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_list(request):
    queryset = get_projects_with_tasks_queryset(
        request.user.fund)
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)
    page = wrap_dicts_page_to_objects_page(
        paginator.get_page(request.GET.get('page')), model=Project)
    return render(request, 'projects_list.html', {
        'page': page
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_details(request, id):
    default_tab = 'tasks'
    page_number = request.GET.get('page')
    tabs = {
        'tasks': lambda project: get_page(
            project.tasks.
            select_related(
                'assignee', 'expense',
                'expense__approvement',
                'assignee__volunteer_profile')
            .order_by('order_position'), page_number),
        'processes': lambda project: get_wrapped_page(
            Process, get_project_processes_with_tasks_queryset(project), page_number),
        'wards': lambda project: get_wrapped_page(
            Ward, get_project_wards_with_tasks_queryset(project), page_number),
        'reviewers': lambda project: get_wrapped_page(
            User, get_project_rewiewers_with_tasks_queryset(project), page_number)
    }

    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    project = get_object_or_404(Project.objects.filter(
        fund=request.user.fund), pk=id)

    page, count = tabs.get(tab)(project)

    return render(request, 'project_details.html', {
        'title': 'Project',
        'tabs': tabs.keys(),
        'items_count': count,
        'project': project,
        'selected_tab': tab,
        'page': page
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_reviewer_details(request, id, reviewer_id):
    project = get_object_or_404(Project.objects.filter(
        fund=request.user.fund), pk=id)

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
