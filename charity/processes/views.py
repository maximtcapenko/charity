from django.db import models
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods, require_GET
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functional import user_should_be_volunteer, render_generic_form, DictObjectWrapper

from .forms import CreateProcessForm, CreateProcessStateForm
from .models import Process, ProcessState


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def create(request):
    return render_generic_form(
        request=request, form_class=CreateProcessForm,
        context={
            'title': 'Add process',
            'return_url': f'{reverse("processes:get_list")}',
            'initial': {
                'fund': request.user.fund
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_details(request, id):
    process = get_object_or_404(
        Process.objects.filter(
            fund=request.user.fund), pk=id)
    return render_generic_form(
        request=request, form_class=CreateProcessForm,
        context={
            'title': 'Edit process',
            'return_url': reverse('processes:get_details', args=[process.id]),
            'initial': {
                'fund': request.user.fund
            },
            'instance': process
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
                    fund=request.user.fund), pk=id)
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_state_details(request, id, state_id):
    process = get_object_or_404(Process.objects.filter(
        fund=request.user.fund), pk=id)
    return render_generic_form(
        request=request, form_class=CreateProcessStateForm, context={
            'title': 'Edit process state',
            'return_url': reverse('processes:get_details', args=[id]),
            'instance': get_object_or_404(process.states, pk=state_id),
            'initial':  {
                'process': process
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_list(request):
    queryset = Process.objects.filter(
        models.Q(fund_id=request.user.fund.id)) \
        .annotate(states_count=models.Count('states', distinct=True)) \
        .values('id', 'name', 'date_created', 'is_inactive', 'states_count') \
        .all()

    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)
    return render(request, 'processes_list.html', {
        'title': 'Processes',
        'items_count': paginator.count,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_details(request, id):
    process = get_object_or_404(
        Process.objects
        .annotate(
            active_project_count=models.Count('projects', distinct=True))
        .values('id', 'name', 'date_created',
                'is_inactive', 'notes', 'active_project_count'), pk=id)

    return render(request, 'process_details.html', {
        'process': DictObjectWrapper(process),
        'states': ProcessState.objects.filter(process__id=process['id']).all()
    })
