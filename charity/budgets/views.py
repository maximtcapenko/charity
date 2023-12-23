from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator

from commons.functions import user_should_be_volunteer
from .models import Budget

default_page_size = 50


@login_required
@user_passes_test(user_should_be_volunteer)
def get_list(request):
    paginator = Paginator(Budget.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id) \
            .order_by('start_period_date'), default_page_size)
    return render(request, 'budgets_list.html', {
        'budget_page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    budget = get_object_or_404(Budget.objects.filter(\
        fund_id=request.user.volunteer_profile.fund_id), pk=id)

    return render(request, 'budget_details.html', {
        'budget': budget,
    })
