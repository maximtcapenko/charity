from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, render_generic_form
from .models import Budget, Income
from .forms import CreateBudgetForm, CreateIncomeForm


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    return render_generic_form(
        request=request, form_class=CreateBudgetForm,
        context={
            'return_url': reverse('funds:get_current_details'),
            'title': 'Add budget',
            'post_form_initial': {
                'user': request.user,
                'fund': request.user.volunteer_profile.fund
            },
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def create_budget_income(request, id):
    budget = get_object_or_404(
        Budget.objects.filter(fund__id=request.user.volunteer_profile.fund_id),
        pk=id)

    return render_generic_form(
        request=request, form_class=CreateIncomeForm,
        context={
            'return_url': reverse('budgets:get_details', args=[budget.id]),
            'title': 'Add income',
            'post_form_initial': {
                'user': request.user,
            },
            'get_form_initial': {
                'budget': budget
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_income_details(request, id):
    income = get_object_or_404(Income.objects.filter(
        budget__fund__id=request.user.volunteer_profile.fund_id), pk=id)

    paginator = Paginator(income.approvements.order_by('-date_created'),
                          DEFAULT_PAGE_SIZE)

    return render(request, 'income_details.html', {
        'income': income,
        'page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_list(request):
    paginator = Paginator(Budget.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id)
        .order_by('start_period_date'), DEFAULT_PAGE_SIZE)
    return render(request, 'budgets_list.html', {
        'page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    default_tab = 'incomes'
    tabs = {
        'incomes': lambda budget: Paginator(
            budget.incomes
                  .select_related('author', 'approvement')
                  .order_by('-date_created'),
            DEFAULT_PAGE_SIZE
        ),
        'expenses': lambda budget: Paginator(
            budget.expenses
            .select_related('author', 'approvement', 'project')
            .order_by('-date_created'),
            DEFAULT_PAGE_SIZE
        )
    }

    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    budget = get_object_or_404(Budget.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)

    paginator = tabs.get(tab)(budget)

    return render(request, 'budget_details.html', {
        'budget': budget,
        'selected_tab': tab,
        'page': paginator.get_page(request.GET.get('page'))
    })
