from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.exceptions import ApplicationError
from commons.functions import render_generic_form, user_should_be_volunteer
from .forms import CreateProjectForm, AddWardToProjectForm, \
    AddProcessToProjectForm, UpdateProjectForm, AddProjectReviewerForm
from .models import Project


def _get_project_or_404(request, project_id):
    return get_object_or_404(
        Project.objects.filter(
            fund__id=request.user.volunteer_profile.fund_id),
        pk=project_id)


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def add_ward_to_project(request, id):
    project = _get_project_or_404(request=request, project_id=id)
    return_url = reverse('projects:get_details', args=[
        project.id]) + '?tab=wards'

    return render_generic_form(
        request=request, form_class=AddWardToProjectForm,
        context={
            'return_url': return_url,
            'title': 'Include ward to project',
            'get_form_initial': {
                'project': project
            },
            'post_form_initial': {
                'project': project
            }
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def add_process_to_project(request, id):
    project = _get_project_or_404(request=request, project_id=id)
    return_url = reverse('projects:get_details', args=[
        project.id]) + '?tab=processes'

    return render_generic_form(
        request=request, form_class=AddProcessToProjectForm,
        context={
            'return_url': return_url,
            'title': 'Include process to project',
            'get_form_initial': {
                'project': project
            },
            'post_form_initial': {
                'project': project
            }
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def edit_details(request, id):
    project = _get_project_or_404(request=request, project_id=id)
    return render_generic_form(
        request=request, form_class=UpdateProjectForm, context={
            'return_url': reverse('projects:get_details', args=[project.id]),
            'title': 'Update project',
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            },
            'post_form_initial': {
                'fund': request.user.volunteer_profile.fund
            },
            'instance': project
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def close(request, id):
    project = get_object_or_404(Project, pk=id)
    return HttpResponseNotAllowed([request.method])


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    return render_generic_form(
        request=request, form_class=CreateProjectForm,
        context={
            'return_url': '%s?%s' % (reverse('funds:get_current_details'), 'tab=projects'),
            'title': 'Add project',
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            }
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def add_project_reviewer(request, id):
    initial = {
        'project': _get_project_or_404(request, id)
    }
    return render_generic_form(
        request=request, form_class=AddProjectReviewerForm, context={
            'return_url': f'{reverse("projects:get_details", args=[id])}?tab=reviewers',
            'title': 'Add project reviewer',
            'get_form_initial': initial,
            'post_form_initial': initial
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def remove_project_reviewer(request, id, reviewer_id):
    project = _get_project_or_404(request, id)
    return_url = f'{reverse("projects:get_details", args=[id])}?tab=reviewers'

    if project.tasks.filter(expense__approvement__author__id=reviewer_id).exists():
        raise ApplicationError(
            'Reviewer has reviewed tasks in project', return_url)

    if project.reviewers.count() == 1:
        """redirect to error page with return url"""
        raise ApplicationError(
            'Project must have at least one reviewer', return_url)

    reviewer = get_object_or_404(project.reviewers, pk=reviewer_id)
    project.reviewers.remove(reviewer)

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_list(request):
    projects = Project.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id).all()

    return render(request, 'projects_list.html', {
        'projects': projects
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_details(request, id):
    default_tab = 'tasks'
    tabs = {
        'tasks': lambda projrect:
            project.tasks.
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

    return render(request, 'project_details.html', {
        'tabs': tabs.keys(),
        'project': project,
        'selected_tab': tab,
        'page': paginator.get_page(request.GET.get('page'))
    })
