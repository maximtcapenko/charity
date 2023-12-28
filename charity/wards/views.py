from django.db import models
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer
from .forms import CreateWardForm
from .models import Ward


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    if request.method == 'POST':
        form = CreateWardForm(request.POST)

        if form.is_valid():
            ward = form.save()
            return redirect(reverse('wards:wards_list', args=[str(ward.fund_id)]))
        else:
            return render(request, 'ward_create.html', {
                'form': form
            })
    elif request.method == 'GET':
        return render(request, 'ward_create.html', {
            'form': CreateWardForm(initial={
                'fund': request.user.volunteer_profile.fund
            })
        })
    else:
        return render(request, "405.html", status=405)


@login_required
@user_passes_test(user_should_be_volunteer)
def get_list(request):
    query_set = Ward.objects.filter(models.Q(fund_id=request.user.volunteer_profile.fund_id),
                                    models.Q(projects__isnull=True) |
                                    models.Q(projects__is_closed=False)) \
        .annotate(active_project_count=models.Count('projects')) \
        .values('id', 'name', 'date_created', 'active_project_count') \
        .all()
    
    paginator = Paginator(query_set, DEFAULT_PAGE_SIZE)
    return render(request, 'wards_list.html', {
        'wards_page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    ward = get_object_or_404(Ward.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)

    return render(request, 'ward_details.html', {
        'ward': ward,
    })
