from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import render_generic_form, user_should_be_volunteer
from .forms import CreateProjectForm, AddWardToProjectForm, \
    AddProcessToProjectForm, UpdateProjectForm
from .models import Project


def _get_project_or_404(request, project_id):
    return get_object_or_404(
        Project.objects.filter(
            fund__id=request.user.volunteer_profile.fund_id),
        pk=project_id)


@login_required
@user_passes_test(user_should_be_volunteer)
def add_ward_to_project(request, id):
    project = _get_project_or_404(request=request, project_id=id)
    return_url = reverse('projects:get_details', args=[
        project.id]) + '?tab=wards'

    return render_generic_form(
        request=request, form_class=AddWardToProjectForm, context={
            'return_url': return_url,
            'title': 'Include ward to project',
            'get_form_initial': {
                'project': project
            },
            'post_form_initial': {
                'project': project
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def add_process_to_project(request, id):
    project = _get_project_or_404(request=request, project_id=id)
    return_url = reverse('projects:get_details', args=[
        project.id]) + '?tab=processes'

    return render_generic_form(
        request=request, form_class=AddProcessToProjectForm, context={
            'return_url': return_url,
            'title': 'Include process to project',
            'get_form_initial': {
                'project': project
            },
            'post_form_initial': {
                'project': project
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def update(request, id):
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


@login_required
@user_passes_test(user_should_be_volunteer)
def close(request, id):
    project = get_object_or_404(Project, pk=id)
    return HttpResponseNotAllowed([request.method])


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    return render_generic_form(
        request=request, form_class=CreateProjectForm, context={
            'return_url': reverse('funds:get_current_details'),
            'title': 'Add project',
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_list(request):
    projects = Project.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id).all()

    return render(request, 'projects_list.html', {
        'projects': projects
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    default_tab = 'tasks'
    tabs = {
        'tasks': lambda projrect: Paginator(
            project.tasks.
            select_related(
                'assignee', 'expense',
                'expense__approvement')
            .order_by('order_position'),
            DEFAULT_PAGE_SIZE),
        'processes': lambda project: Paginator(
            project.processes.order_by('-date_created'),
            DEFAULT_PAGE_SIZE
        ),
        'wards': lambda project: Paginator(
            project.wards.order_by('-date_created'),
            DEFAULT_PAGE_SIZE
        )
    }

    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    project = get_object_or_404(Project.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)

    paginator = tabs.get(tab)(project)

    return render(request, 'project_details.html', {
        'tabs': tabs.keys(),
        'project': project,
        'selected_tab': tab,
        'page': paginator.get_page(request.GET.get('page'))
    })
