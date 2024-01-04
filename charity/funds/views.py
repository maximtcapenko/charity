from django.db import models
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.urls import reverse
from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, user_should_be_superuser, \
    render_generic_form
from .models import Fund
from .forms import CreateContributionForm, CreateVolunteerForm, CreateContributorForm


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
    default_tab = 'contributions'
    tabs = {
        'contributions': lambda fund: Paginator(
            fund.contributions.select_related(
                'author', 'contributor').order_by('-date_created'),
            DEFAULT_PAGE_SIZE),
        'contributors': lambda fund: Paginator(
            fund.contributors.order_by('-date_created'),
            DEFAULT_PAGE_SIZE
        ),
        'budgets': lambda fund: Paginator(
            fund.budgets.order_by('-date_created'),
            DEFAULT_PAGE_SIZE),
        'projects': lambda fund: Paginator(
            fund.active_projects.order_by('-date_created'),
            DEFAULT_PAGE_SIZE),
        'processes': lambda fund: Paginator(
            fund.processes.annotate(active_project_count=models.Count('projects', distinct=True),
                                    states_count=models.Count('states', distinct=True))
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
        'tabs': tabs.keys(),
        'page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_current_details(request):
    return get_details(request, request.user.volunteer_profile.fund_id)


@login_required
@user_passes_test(user_should_be_volunteer)
def add_contribution(request):
    return render_generic_form(
        request=request,
        form_class=CreateContributionForm,
        context={
            'title': 'Add contribution',
            'return_url': '%s?%s' % (reverse('funds:get_current_details'), 'tab=contributions'),
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            },
            'post_form_initial': {
                'fund': request.user.volunteer_profile.fund,
                'user': request.user
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def add_volunteer(request):
    return render_generic_form(
        request=request,
        form_class=CreateVolunteerForm,
        context={
            'title': 'Add volunteer',
            'return_url': '%s?%s' % (reverse('funds:get_current_details'), 'tab=volunteers'),
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            },
            'post_form_initial': {
                'fund': request.user.volunteer_profile.fund
            }
        }
    )


@login_required
@user_passes_test(user_should_be_volunteer)
def add_contributor(request):
    return render_generic_form(
        request=request,
        form_class=CreateContributorForm,
        context={
            'title': 'Add contributor',
            'return_url': '%s?%s' % (reverse('funds:get_current_details'), 'tab=contributors'),
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            },
            'post_form_initial': {
                'fund': request.user.volunteer_profile.fund
            }
        }
    )


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
