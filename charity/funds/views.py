from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, user_should_be_superuser
from .models import Fund
from django.db import models
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator


@login_required
@user_passes_test(user_should_be_superuser)
def get_list(request):
    paginator = Paginator(Fund.objects.order_by('id'), DEFAULT_PAGE_SIZE)
    return render(request, 'funds_list.html', {
        'fund_page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    default_tab = 'budgets'
    tabs = {
        'contributions': lambda fund: Paginator(
            fund.contributions.select_related('author', 'contributor').order_by('-date_created'), DEFAULT_PAGE_SIZE),
        'projects': lambda fund: Paginator(
            fund.active_projects.order_by('-date_created'), DEFAULT_PAGE_SIZE),
        'budgets': lambda fund: Paginator(
            fund.budgets.order_by('-start_period_date'), DEFAULT_PAGE_SIZE),
        'processes': lambda fund: Paginator(
            fund.processes.annotate(active_project_count=models.Count('projects'),
                                    states_count=models.Count('states'))
            .order_by('-date_created')
            .values('id', 'name', 'date_created', 'is_inactive',
                    'states_count', 'active_project_count'), DEFAULT_PAGE_SIZE),
        'volunteers': lambda fund: Paginator(
            fund.volunteers.order_by('-date_created'), DEFAULT_PAGE_SIZE)
    }

    fund = get_object_or_404(Fund, pk=id)
    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    paginator = tabs.get(tab)(fund)

    return render(request, 'fund_details.html', {
        'fund': fund,
        'selected_tab': tab,
        'page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_current_details(request):
    return get_details(request, request.user.volunteer_profile.fund_id)


@login_required
@user_passes_test(user_should_be_volunteer)
def update_details(request, id):
    if request.method == 'POST':
        pass
    else:
        pass
    return render(request, 'fund_details.html', {
        'fund': Fund.objects.get(pk=id)
    })
