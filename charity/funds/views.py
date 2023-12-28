from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, user_should_be_superuser
from .models import Fund
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator



@login_required
@user_passes_test(user_should_be_superuser)
def get_list(request):
    paginator = Paginator(Fund.objects.order_by('id'),
                          per_page=DEFAULT_PAGE_SIZE)
    return render(request, 'funds_list.html', {
        'fund_page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    fund = get_object_or_404(Fund, pk=id)
    paginator = Paginator(fund.active_projects.order_by(
        'date_created'), per_page=10)

    return render(request, 'fund_details.html', {
        'fund': fund,
        'active_projects_page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_current_details(request):
    fund = get_object_or_404(Fund.objects.filter(id=request.user.volunteer_profile.fund_id))
    
    paginator = Paginator(fund.active_projects.order_by(
        'date_created'), DEFAULT_PAGE_SIZE)

    return render(request, 'fund_details.html', {
        'fund': fund,
        'active_projects_page': paginator.get_page(request.GET.get('page'))
    })


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
