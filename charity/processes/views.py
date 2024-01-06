from django.db import models
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, render_generic_form

from .forms import CreateProcessForm, CreateProcessStateForm
from .models import Process


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    return render_generic_form(
        request=request, form_class=CreateProcessForm,
        context={
            'title': 'Add process',
            'return_url': reverse('processes:get_list'),
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def create_state(request, id):
    return render_generic_form(
        request=request, form_class=CreateProcessStateForm, context={
            'title': 'Add process state',
            'return_url': reverse('processes:get_details', args=[id]),
            'get_form_initial':  {
                'process': get_object_or_404(Process.objects.filter(
                    fund__id=request.user.volunteer_profile.fund_id), pk=id)
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_list(request):
    query_set = Process.objects.filter(models.Q(fund_id=request.user
                                                .volunteer_profile.fund_id),
                                       models.Q(projects__isnull=True) |
                                       models.Q(projects__is_closed=False)) \
        .annotate(active_project_count=models.Count('projects', distinct=True),
                  states_count=models.Count('states', distinct=True)) \
        .order_by('-date_created') \
        .values('id', 'name', 'date_created', 'is_inactive',
                'states_count', 'active_project_count') \
        .all()

    paginator = Paginator(query_set, DEFAULT_PAGE_SIZE)
    return render(request, 'processes_list.html', {
        'processes_page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    process = get_object_or_404(Process, pk=id)
    paginator = Paginator(process.states.order_by(
        'order_position'), DEFAULT_PAGE_SIZE)

    return render(request, 'process_details.html', {
        'process': process,
        'states_page': paginator.get_page(request.GET.get('page'))
    })
