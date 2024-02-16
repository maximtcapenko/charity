from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from commons import DEFAULT_PAGE_SIZE
from commons.exceptions import ApplicationError
from commons.functional import user_should_be_volunteer, user_should_be_superuser, \
    render_generic_form, wrap_dicts_page_to_objects_page

from budgets.models import Income

from .querysets import get_contributor_budgets_queryset, get_contributions_queryset, \
    get_contribution_details_queryset
from .messages import Warnings
from .models import Contribution, Contributor, Fund, VolunteerProfile
from .forms import CreateContributionForm, CreateVolunteerForm, \
    CreateContributorForm, UpdateVolunteerProfile
from .requirements import contribution_is_ready_to_be_removed


@user_passes_test(user_should_be_superuser)
@require_GET
def get_list(request):
    paginator = Paginator(Fund.objects.order_by('id'), DEFAULT_PAGE_SIZE)
    return render(request, 'funds_list.html', {
        'fund_page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_details(request, id):
    default_tab = 'contributions'
    tabs = {
        'contributions': lambda fund: get_contributions_queryset(fund),
        'contributors': lambda fund: fund.contributors.all(),
        'volunteers': lambda fund: fund.volunteers.all(),
    }

    fund = get_object_or_404(Fund, pk=id)
    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    queryset = tabs.get(tab)(fund)
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    if tab == 'contributions':
        page = wrap_dicts_page_to_objects_page(
            paginator.get_page(request.GET.get('page')), model=Contribution)
    else:
        page = paginator.get_page(request.GET.get('page'))

    return render(request, 'fund_details.html', {
        'title': 'Fund',
        'fund': fund,
        'selected_tab': tab,
        'items_count': paginator.count,
        'tabs': tabs.keys(),
        'page': page
    })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_get_current_details_partial(request,  *args, **kwargs):
    return render(request, 'partials/fund_details.html', {
        'title': kwargs.get('title'),
        'fund': get_object_or_404(Fund, pk=request.user.fund.id)
    })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_current_details(request):
    return get_details(request, request.user.fund.id)


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
                'fund': request.user.fund
            }
        }
    )


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_contributor_details(request, id):
    contributor = get_object_or_404(
        Contributor.objects.filter(
            fund=request.user.fund), pk=id)

    queryset = get_contributor_budgets_queryset(contributor)

    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)
    page = wrap_dicts_page_to_objects_page(
        paginator.get_page(request.GET.get('page')))

    return render(request, 'fund_contributor_details.html', {
        'contributor': contributor,
        'page': page
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_contributor_details(request, id):
    return render_generic_form(request, form_class=CreateContributorForm, context={
        'title': 'Edit contributor',
        'return_url': reverse('funds:get_contributor_details', args=[id]),
        'initial': {
            'fund': request.user.fund
        },
        'instance': get_object_or_404(
            Contributor.objects.filter(
                fund=request.user.fund),
            pk=id)
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
                'fund': request.user.fund,
                'author': request.user
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_contribution_details(request, id):
    contribution = get_object_or_404(
        Contribution.objects.filter(
            fund=request.user.fund),
        pk=id)
    queryset = get_contribution_details_queryset(contribution)

    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)
    page = wrap_dicts_page_to_objects_page(
        paginator.get_page(request.GET.get('page')), model=Income)
    return render(request, 'fund_contribution_details.html', {
        'title': 'Contribution',
        'contribution': contribution,
        'page': page
    })


@user_passes_test(user_should_be_volunteer)
@require_POST
def remove_contribution(request, id):
    return_url = f'{reverse("funds:get_current_details")}?tab=contributions'
    contribution = get_object_or_404(request.user.fund.contributions, pk=id)
    if not contribution_is_ready_to_be_removed(contribution, request.user):
        raise ApplicationError(
            Warnings.CONTRIBUTION_IS_NOT_READY_TOBE_REMOVED, return_url)

    if contribution.contributor.is_internal:
        if contribution.tasks.filter(project__is_closed=True).exists():
            raise ApplicationError(
                Warnings.CONTRIBUTION_IS_INTERNAL_AND_LINKED_PROJECT_IS_CLOSED, return_url)

    contribution.delete()
    return redirect(return_url)


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
                'fund': request.user.fund
            }
        }
    )


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_volunteer_details(request, id):
    volunteer = get_object_or_404(
        VolunteerProfile.objects.filter(
            fund=request.user.fund),
        pk=id)
    return render(request, 'fund_volunteer_details.html', {
        'volunteer': volunteer
    })


@user_passes_test(user_should_be_volunteer)
@require_POST
def add_volunteer_cover(request, id):
    cover = request.FILES['cover']
    if cover:
        volunteer = get_object_or_404(
            VolunteerProfile.objects.filter(
                fund=request.user.fund), pk=id)
        volunteer.cover = cover
        volunteer.save()

    return redirect(reverse('funds:get_volunteer_details', args=[id]))


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_volunteer_profile(request, id):
    volunteer = get_object_or_404(
        VolunteerProfile.objects.filter(
            fund__id=request.user.fund.id), pk=id)

    return render_generic_form(
        request=request, form_class=UpdateVolunteerProfile,
        context={
            'title': 'Edit volunteer',
            'return_url': reverse('funds:get_volunteer_details', args=[id]),
            'instance': volunteer,
            'initial': {
                'fund': request.user.fund
            },
        })
