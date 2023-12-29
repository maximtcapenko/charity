from django.http import HttpResponseNotAllowed
from django.db import models
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer

from .forms import CreateProcessForm, CreateProcessStateForm
from .models import Process


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    if request.method == 'POST':
        form = CreateProcessForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse('processes:get_list'))
        else:
            return render(request, 'generic_createform.html', {
                'title': 'Add process',
                'return_url': reverse('processes:get_list'),
                'form': form
            })
    elif request.method == 'GET':
        return render(request, 'generic_createform.html', {
            'title': 'Add process',
            'return_url': reverse('processes:get_list'),
            'form': CreateProcessForm(initial={
                'fund': request.user.volunteer_profile.fund
            })
        })
    else:
        return HttpResponseNotAllowed([request.method])


@login_required
@user_passes_test(user_should_be_volunteer)
def create_state(request, id):
    if request.method == 'POST':
        form = CreateProcessStateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('processes:get_details', args=[id]))
        else:
            return render(request, 'generic_createform.html', {
                'title': 'Add process state',
                'return_url': reverse('processes:get_details', args=[id]),
                'form': form
            })
    elif request.method == 'GET':
        form = CreateProcessStateForm(initial={
            'process': get_object_or_404(Process, pk=id)
        })
        return render(request, 'generic_createform.html', {
            'title': 'Add process state',
            'return_url': reverse('processes:get_details', args=[id]),
            'form': form
        })
    else:
        return HttpResponseNotAllowed([request.method])


@login_required
@user_passes_test(user_should_be_volunteer)
def get_list(request):
    query_set = Process.objects.filter(models.Q(fund_id=request.user
                                                .volunteer_profile.fund_id),
                                       models.Q(projects__isnull=True) |
                                       models.Q(projects__is_closed=False)) \
        .annotate(active_project_count=models.Count('projects'),
                  states_count=models.Count('states')) \
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
        'date_created'), DEFAULT_PAGE_SIZE)

    return render(request, 'process_details.html', {
        'process': process,
        'states_page': paginator.get_page(request.GET.get('page'))
    })
