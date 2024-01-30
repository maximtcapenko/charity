from django.db import models
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, render_generic_form, \
    wrap_dicts_page_to_objects_page
from .forms import CreateWardForm
from .models import Ward
from projects.models import Project
from tasks.models import Task


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def add_ward_cover(request, id):
    cover = request.FILES['cover']
    if cover:
        ward = get_object_or_404(
            Ward.objects.filter(
                fund__id=request.user.volunteer_profile.fund_id),
            pk=id)
        ward.cover = cover
        ward.save()

    return redirect(reverse('wards:get_details', args=[id]))


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    return render_generic_form(
        request=request, form_class=CreateWardForm, context={
            'title': 'Add ward',
            'return_url': reverse('wards:get_list'),
            'initial': {
                'fund': request.user.volunteer_profile.fund
            }
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def edit_details(request, id):
    ward = get_object_or_404(Ward.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)
    
    return render_generic_form(
        request=request, form_class=CreateWardForm, context={
            'title': 'Add ward',
            'return_url': reverse('wards:get_details', args=[ward.id]),
            'initial': {
                'fund': request.user.volunteer_profile.fund
            },
            'instance': ward
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_list(request):
    """ 
    project_subquery = Project.objects.filter(wards__in=models.OuterRef('pk'), is_closed=False)\
    .values('name')[:1]
    """
    queryset = Ward.objects.filter(fund_id=request.user.volunteer_profile.fund_id)\
        .prefetch_related(models.Prefetch('projects', Project.objects.filter(is_closed=False)))

    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    return render(request, 'wards_list.html', {
        'page': wrap_dicts_page_to_objects_page(paginator.get_page(request.GET.get('page')), model=Ward)
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_details(request, id):
    ward = get_object_or_404(Ward.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)

    return render(request, 'ward_details.html', {
        'ward': ward,
        'title': 'Ward'
    })
