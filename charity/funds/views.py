from django.db import models
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, user_should_be_superuser, \
    render_generic_form
from .models import Contribution, Contributor, Fund, VolunteerProfile
from .forms import CreateContributionForm, CreateVolunteerForm, \
    CreateContributorForm, UpdateVolunteerProfile


@user_passes_test(user_should_be_superuser)
@require_http_methods(['GET'])
def get_list(request):
    paginator = Paginator(Fund.objects.order_by('id'), DEFAULT_PAGE_SIZE)
    return render(request, 'funds_list.html', {
        'fund_page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_details(request, id):
    default_tab = 'contributions'
    tabs = {
        'contributions': lambda fund: fund.contributions
        .select_related(
            'author', 'author__volunteer_profile', 'contributor'),
        'contributors': lambda fund: fund.contributors.all(),
        'volunteers': lambda fund: fund.volunteers.all(),
    }

    fund = get_object_or_404(Fund, pk=id)
    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    queryset = tabs.get(tab)(fund)
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    return render(request, 'fund_details.html', {
        'title': 'Fund',
        'fund': fund,
        'selected_tab': tab,
        'items_count': paginator.count,
        'tabs': tabs.keys(),
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_get_current_details_partial(request,  *args, **kwargs):
    return render(request, 'partials/fund_details.html', {
        'title': kwargs.get('title'),
        'fund': get_object_or_404(Fund, pk=request.user.volunteer_profile.fund_id)
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_current_details(request):
    return get_details(request, request.user.volunteer_profile.fund_id)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_contribution_details(request, id):
    contribution = get_object_or_404(
        Contribution.objects.filter(
            fund_id=request.user.volunteer_profile.fund_id),
        pk=id)
    query_set = contribution.incomes.values('budget__id', 'budget__name').annotate(
        budget_amount=models.Sum('amount', default=0))

    paginator = Paginator(query_set, DEFAULT_PAGE_SIZE)
    return render(request, 'fund_contribution_details.html', {
        'title': 'Contribution',
        'contribution': contribution,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_contributor_details(request, id):
    contributor = get_object_or_404(
        Contributor.objects.filter(
            fund_id=request.user.volunteer_profile.fund_id),
        pk=id)

    query_set = contributor.contributions.filter(incomes__isnull=False) \
        .select_related('incomes') \
        .values('incomes__budget__id', 'incomes__budget__name') \
        .annotate(budget_amount=models.Sum('incomes__amount', default=0))

    paginator = Paginator(query_set, DEFAULT_PAGE_SIZE)
    return render(request, 'fund_contributor_details.html', {
        'contributor': contributor,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_volunteer_details(request, id):
    volunteer = get_object_or_404(
        VolunteerProfile.objects.filter(
            fund__id=request.user.volunteer_profile.fund_id),
        pk=id)
    return render(request, 'fund_volunteer_details.html', {
        'volunteer': volunteer
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def add_volunteer_cover(request, id):
    cover = request.FILES['cover']
    if cover:
        volunteer = get_object_or_404(
            VolunteerProfile.objects.filter(
                fund__id=request.user.volunteer_profile.fund_id),
            pk=id)
        volunteer.cover = cover
        volunteer.save()

    return redirect(reverse('funds:get_volunteer_details', args=[id]))


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_contributor_details(request, id):
    return render_generic_form(request, form_class=CreateContributorForm, context={
        'title': 'Edit contributor',
        'return_url': reverse('funds:get_contributor_details', args=[id]),
        'initial': {
            'fund': request.user.volunteer_profile.fund
        },
        'instance': get_object_or_404(
            Contributor.objects.filter(
                fund_id=request.user.volunteer_profile.fund_id),
            pk=id)
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_volunteer_profile(request, id):
    volunteer = get_object_or_404(
        VolunteerProfile.objects.filter(
            fund__id=request.user.volunteer_profile.fund_id),
        pk=id)

    return render_generic_form(
        request=request, form_class=UpdateVolunteerProfile,
        context={
            'title': 'Edit volunteer',
            'return_url': reverse('funds:get_volunteer_details', args=[id]),
            'instance': volunteer,
            'initial': {
                'fund': request.user.volunteer_profile.fund
            },
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_contribution(request):
    return render_generic_form(
        request=request,
        form_class=CreateContributionForm,
        context={
            'title': 'Add contribution',
            'return_url': '%s?%s' % (reverse('funds:get_current_details'), 'tab=contributions'),
            'initial': {
                'fund': request.user.volunteer_profile.fund,
                'author': request.user
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_volunteer(request):
    return render_generic_form(
        request=request,
        form_class=CreateVolunteerForm,
        context={
            'title': 'Add volunteer',
            'return_url': '%s?%s' % (reverse('funds:get_current_details'), 'tab=volunteers'),
            'initial': {
                'fund': request.user.volunteer_profile.fund
            }
        }
    )


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_contributor(request):
    return render_generic_form(
        request=request,
        form_class=CreateContributorForm,
        context={
            'title': 'Add contributor',
            'return_url': '%s?%s' % (reverse('funds:get_current_details'), 'tab=contributors'),
            'initial': {
                'fund': request.user.volunteer_profile.fund
            }
        }
    )