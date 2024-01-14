from django.db import models
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, render_generic_form
from .forms import CreateWardForm
from .models import Ward
from projects.models import Project


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
@require_http_methods(['GET'])
def get_list(request):
    total_count = Ward.objects.count()
    total_active_count = Ward.active_objects.count()
    total_count_in_projects = Ward.active_objects.filter(models.Exists(
        Project.objects.filter(wards__in=models.OuterRef('pk'), is_closed=False))).count()

    query_set = Ward.objects.filter(models.Q(fund_id=request.user.volunteer_profile.fund_id),
                                    models.Q(projects__isnull=True) |
                                    models.Q(projects__is_closed=False)) \
        .annotate(active_project_count=models.Count('projects')) \
        .values('id', 'name', 'date_created', 'is_inactive', 'active_project_count') \
        .all()

    paginator = Paginator(query_set, DEFAULT_PAGE_SIZE)
    return render(request, 'wards_list.html', {
        'total_count': total_count,
        'total_active_count': total_active_count,
        'total_count_in_projects': total_count_in_projects,
        'wards_page': paginator.get_page(request.GET.get('page'))
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
