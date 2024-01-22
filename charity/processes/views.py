from django.db import models
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, render_generic_form

from .forms import CreateProcessForm, UpdateProcessForm, CreateProcessStateForm
from .models import Process, ProcessState


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def create(request):
    return render_generic_form(
        request=request, form_class=CreateProcessForm,
        context={
            'title': 'Add process',
            'return_url': f'{reverse("funds:get_details")}?tab=processes',
            'initial': {
                'fund': request.user.volunteer_profile.fund
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def create_state(request, id):
    return render_generic_form(
        request=request, form_class=CreateProcessStateForm, context={
            'title': 'Add process state',
            'return_url': reverse('processes:get_details', args=[id]),
            'initial':  {
                'process': get_object_or_404(Process.objects.filter(
                    fund__id=request.user.volunteer_profile.fund_id), pk=id)
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_details(request, id):
    process = get_object_or_404(
        Process.objects.filter(
            fund__id=request.user.volunteer_profile.fund_id), pk=id)
    return render_generic_form(
        request=request, form_class=UpdateProcessForm,
        context={
            'title': 'Edit process',
            'return_url': reverse('processes:get_details', args=[process.id]),
            'initial': {
                'fund': request.user.volunteer_profile.fund
            },
            'instance': process
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_list(request):
    queryset = Process.objects.filter(
        models.Q(fund_id=request.user.volunteer_profile.fund_id),
        models.Q(projects__isnull=True) |
        models.Q(projects__is_closed=False)) \
        .annotate(active_project_count=models.Count('projects', distinct=True),
                  states_count=models.Count('states', distinct=True)) \
        .values('id', 'name', 'date_created', 'is_inactive',
                'states_count', 'active_project_count') \
        .all()

    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)
    return render(request, 'processes_list.html', {
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_details(request, id):
    process = get_object_or_404(
        Process.objects
        .annotate(
            active_project_count=models.Count('projects', distinct=True))
        .values('id', 'name', 'date_created',
                'is_inactive', 'notes', 'active_project_count'), pk=id)

    return render(request, 'process_details.html', {
        'process': process,
        'states': ProcessState.objects.filter(process__id=process['id']).all()
    })
