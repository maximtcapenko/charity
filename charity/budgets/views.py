from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer
from .models import Budget
from .forms import CreateBudgetForm


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    return_url = reverse('funds:get_current_details')
    title = 'Add budget'

    if request.method == 'POST':
        form = CreateBudgetForm(request.POST, initial={
            'user': request.user,
            'fund': request.user.volunteer_profile.fund
        })

        if form.is_valid():
            budget = form.save()
            return redirect(return_url)
        else:
            return render(request, 'generic_createform.html', {
                'return_url': return_url,
                'title': title,
                'form': form
            })
    elif request.method == 'GET':
        return render(request, 'generic_createform.html', {
            'return_url': return_url,
            'title': title,
            'form': CreateBudgetForm(initial={
                'fund': request.user.volunteer_profile.fund
            })
        })
    else:
        return HttpResponseNotAllowed([request.method])


@login_required
@user_passes_test(user_should_be_volunteer)
def get_list(request):
    paginator = Paginator(Budget.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id)
        .order_by('start_period_date'), DEFAULT_PAGE_SIZE)
    return render(request, 'budgets_list.html', {
        'budget_page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    budget = get_object_or_404(Budget.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)

    return render(request, 'budget_details.html', {
        'budget': budget,
    })
