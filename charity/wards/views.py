from django.db import models
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods, require_GET
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functional import user_should_be_volunteer, render_generic_form
from projects.models import Project

from .forms import CreateWardForm, SearchWardForm
from .models import Ward


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def add_ward_cover(request, id):
    cover = request.FILES['cover']
    if cover:
        ward = get_object_or_404(
            Ward.objects.filter(
                fund=request.user.fund),
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
                'fund': request.user.fund
            }
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def edit_details(request, id):
    ward = get_object_or_404(Ward.objects.filter(
        fund=request.user.fund), pk=id)

    return render_generic_form(
        request=request, form_class=CreateWardForm, context={
            'title': 'Edit ward',
            'return_url': reverse('wards:get_details', args=[ward.id]),
            'initial': {
                'fund': request.user.fund
            },
            'instance': ward
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_GET
def get_list(request):
    queryset = Ward.objects.filter(fund=request.user.fund)
    search_form = SearchWardForm(request.user.fund, request.GET)
    queryset = search_form.get_search_queryset(queryset)

    queryset = queryset.prefetch_related(models.Prefetch(
        'projects', Project.objects.filter(is_closed=False)))

    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    return render(request, 'wards_list.html', {
        'search_form': search_form,
        'page': paginator.get_page(request.GET.get('page')),
        'items_count': paginator.count
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_GET
def get_details(request, id):
    default_tab = 'comments'
    tabs = [
        'comments',
        'files',
        'tasks'
    ]
    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    ward = get_object_or_404(Ward.objects.filter(
        fund=request.user.fund), pk=id)

    return render(request, 'ward_details.html', {
        'ward': ward,
        'tabs': tabs,
        'selected_tab': tab,
        'model_name': ward._meta.model_name,
        'title': 'Ward'
    })
