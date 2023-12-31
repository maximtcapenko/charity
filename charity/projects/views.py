from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer
from .forms import CreateProjectForm, AddWardToProjectForm, \
    AddProcessToProjectForm, UpdateProjectForm
from .models import Project


@login_required
@user_passes_test(user_should_be_volunteer)
def add_ward_to_project(request, id):
    project = get_object_or_404(Project, pk=id)
    return_url = reverse('projects:get_details', args=[
                          project.id]) + '?tab=wards'
    form_title = 'Include ward to project'
    form_template = 'generic_createform.html'

    if request.method == 'POST':
        form = AddWardToProjectForm(request.POST)
        if form.is_valid():
            ward = form.cleaned_data['ward']
            project.wards.add(ward)
            project.save()

            return redirect(return_url)
        else:
            return render(request, form_template, {
                'return_url': return_url,
                'title': form_title,
                'form': form
            })
    elif request.method == 'GET':
        return render(request, form_template, {
            'return_url': return_url,
            'title': form_title,
            'form': AddWardToProjectForm(initial={
                'project': project
            })
        })
    else:
        return HttpResponseNotAllowed([request.method])


@login_required
@user_passes_test(user_should_be_volunteer)
def add_process_to_project(request, id):
    project = get_object_or_404(Project, pk=id)
    return_url = reverse('projects:get_details', args=[
        project.id]) + '?tab=processes'
    form_title = 'Include process to project'
    form_template = 'generic_createform.html'

    if request.method == 'POST':
        form = AddProcessToProjectForm(request.POST)
        if form.is_valid():
            process = form.cleaned_data['process']
            project.processes.add(process)
            project.save()

            return redirect(return_url)
        else:
            return render(request, form_template, {
                'return_url': return_url,
                'title': form_title,
                'form': form
            })
    elif request.method == 'GET':
        return render(request, form_template, {
            'return_url': return_url,
            'title': form_title,
            'form': AddProcessToProjectForm(initial={
                'project': project
            })
        })
    else:
        return HttpResponseNotAllowed([request.method])


@login_required
@user_passes_test(user_should_be_volunteer)
def update(request, id):
    project = get_object_or_404(Project, pk=id)
    return_url = reverse('projects:get_details',
                         args=[project.id])
    form_title = 'Update project'
    form_template = 'generic_createform.html'

    if request.method == 'POST':
        form = UpdateProjectForm(request.POST, instance=project,
                                 initial={
                                     'fund': request.user.volunteer_profile.fund
                                 })
        if form.is_valid():
            form.save()
            return redirect(return_url)
        else:
            return render(request, form_template,
                          {'return_url': return_url,
                           'title': form_title,
                           'form': form
                           })
    elif request.method == 'GET':
        form = UpdateProjectForm(initial={
            'fund': request.user.volunteer_profile.fund
        }, instance=project)
        return render(request, form_template,
                      {'return_url': return_url,
                       'title': form_title,
                       'form': form
                       })
    else:
        return HttpResponseNotAllowed([request.method])


@login_required
@user_passes_test(user_should_be_volunteer)
def close(request, id):
    project = get_object_or_404(Project, pk=id)
    return HttpResponseNotAllowed([request.method])


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    if request.method == 'POST':
        form = CreateProjectForm(request.POST)

        if form.is_valid():
            project = form.save()
            return redirect(reverse('funds:fund_details', args=[str(project.fund_id)]))
        else:
            return render(request, 'generic_createform.html', {
                'return_url': reverse('funds:get_current_details'),
                'title': 'Add project',
                'form': form
            })
    elif request.method == 'GET':
        return render(request, 'generic_createform.html', {
            'return_url': reverse('funds:get_current_details'),
            'title': 'Add project',
            'form': CreateProjectForm(initial={
                'fund': request.user.volunteer_profile.fund
            })
        })
    else:
        return HttpResponseNotAllowed([request.method])


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
    project = get_object_or_404(Project.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)

    tab = request.GET.get('tab', 'tasks')

    paginator = None
    if tab == 'processes':
        paginator = Paginator(
            project.processes.order_by('-date_created'),
            per_page=DEFAULT_PAGE_SIZE
        )
    elif tab == 'wards':
        paginator = Paginator(
            project.wards.order_by('-date_created'),
            per_page=DEFAULT_PAGE_SIZE
        )
    elif tab == 'processes':
        paginator = Paginator(
            project.processes.order_by('-date_created'),
            per_page=DEFAULT_PAGE_SIZE
        )
    else:
        paginator = Paginator(
            project.tasks.
            select_related(
                'assignee', 'expense',
                'expense__approvement')
            .order_by('order_position'), per_page=DEFAULT_PAGE_SIZE)

    return render(request, 'project_details.html', {
        'project': project,
        'selected_tab': tab,
        'page': paginator.get_page(request.GET.get('page'))
    })
