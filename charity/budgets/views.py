import uuid
from django.db import models
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.functions import user_should_be_volunteer, render_generic_form
from .models import Budget, Income
from .forms import CreateBudgetForm, CreateIncomeForm, \
    BudgetItemApproveForm, ApproveBudgetForm
from projects.models import Project
from tasks.models import Task, Expense


def _get_budget_or_404(request, id):
    return get_object_or_404(Budget.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    return render_generic_form(
        request=request, form_class=CreateBudgetForm,
        context={
            'return_url': reverse('funds:get_current_details'),
            'title': 'Add budget',
            'post_form_initial': {
                'fund': request.user.volunteer_profile.fund,
                'user': request.user,
            },
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def create_budget_income(request, id):
    budget = _get_budget_or_404(request, id)

    return render_generic_form(
        request=request, form_class=CreateIncomeForm,
        context={
            'return_url': reverse('budgets:get_details', args=[budget.id]),
            'title': 'Add income',
            'post_form_initial': {
                'user': request.user,
                'budget': budget
            },
            'get_form_initial': {
                'budget': budget
            }
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def approve_budget(request, id):
    return render_generic_form(
        request=request,
        form_class=ApproveBudgetForm, context={
            'return_url': '%s?%s' % (reverse('budgets:get_details', args=[id]),
                                     'tab=approvements'),
            'title': 'Add approvement',
            'post_form_initial': {
                'user': request.user,
                'fund': request.user.volunteer_profile.fund,
                'target': _get_budget_or_404(request, id)
            },
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def approve_budget_income(request, id):
    return render_generic_form(
        request=request,
        form_class=BudgetItemApproveForm, context={
            'return_url': reverse('budgets:get_income_details', args=[id]),
            'title': 'Add approvement',
            'post_form_initial': {
                'user': request.user,
                'fund': request.user.volunteer_profile.fund,
                'target': get_object_or_404(Income.objects.filter(
                    budget__fund__id=request.user.volunteer_profile.fund_id), pk=id)
            },
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def approve_budget_expense(request, id):
    return render_generic_form(
        request=request,
        form_class=BudgetItemApproveForm, context={
            'return_url': reverse('budgets:get_expense_details', args=[id]),
            'title': 'Add approvement',
            'post_form_initial': {
                'user': request.user,
                'fund': request.user.volunteer_profile.fund,
                'target': get_object_or_404(Expense.objects.filter(
                    budget__fund__id=request.user.volunteer_profile.fund_id), pk=id)
            },
        })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_income_details(request, id):
    income = get_object_or_404(Income.objects.filter(
        budget__fund__id=request.user.volunteer_profile.fund_id), pk=id)

    paginator = Paginator(income.approvements.order_by('-date_created'),
                          DEFAULT_PAGE_SIZE)

    return render(request, 'budget_income_details.html', {
        'income': income,
        'page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_expense_details(request, id):
    expense = get_object_or_404(Expense.objects.filter(
        budget__fund__id=request.user.volunteer_profile.fund_id), pk=id)

    paginator = Paginator(expense.approvements.order_by('-date_created'),
                          DEFAULT_PAGE_SIZE)

    return render(request, 'budget_expense_details.html', {
        'expense': expense,
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
        ),
        'approvements': lambda budget: Paginator(
            budget.approvements.order_by('-date_created'),
            DEFAULT_PAGE_SIZE
        )
    }

    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    budget = _get_budget_or_404(request, id)
    total_approved_amount = budget.total_approved_amount
    total_approved_expenses_amount = budget.total_approved_expenses_amount

    paginator = tabs.get(tab)(budget)

    return render(request, 'budget_details.html', {
        'tabs': tabs.keys(),
        'budget': budget,
        'total_approved_amount': total_approved_amount,
        'total_approved_expenses_amount': total_approved_expenses_amount,
        'total_avaliable_amount': total_approved_amount-total_approved_expenses_amount,
        'selected_tab': tab,
        'page': paginator.get_page(request.GET.get('page'))
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def budget_expenses_planing(request, id):
    budget = _get_budget_or_404(request, id)
    if budget.approvement and budget.approvement.is_rejected == False:
        return redirect('%s?%s' % (reverse('budgets:get_details', args=[id]), 'tab=expenses'))
    
    pending_expense_amount = Expense.objects.filter(
        budget_id=budget.id, approvement__isnull=True)\
        .aggregate(pending_expense_amount=models.Sum('amount', default=0))['pending_expense_amount']

    avaliable_income_amount = budget.avaliable_income_amount - pending_expense_amount

    projects = Project.objects.annotate(
        requested_budget=models.Sum('tasks__estimated_expense_amount',
                                    filter=models.Q(tasks__expense__isnull=True), distinct=True, default=0))\
        .filter(is_closed=False, fund_id=budget.fund_id, tasks__isnull=False) \
        .values('id', 'name', 'requested_budget').all()

    tasks = []
    selected_project = request.GET.get('project_id')
    if selected_project:
        project = list(filter(lambda project: project['id'] == uuid.UUID(
            selected_project), projects))[0]
        if project:
            tasks = Task.objects.filter(project_id=project['id'], expense__isnull=True) \
                .only('id', 'name', 'is_high_priority', 'estimated_expense_amount')

    return render(request, 'budget_expenses_planing.html', {
        'budget': budget,
        'avaliable_income_amount': avaliable_income_amount,
        'projects': projects,
        'selected_project': selected_project,
        'tasks': tasks
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def add_budget_expenses(request, id):
    budget = _get_budget_or_404(request, id)
    task_id = request.GET.get('task_id')
    project_id = request.GET.get('project_id')
    project = get_object_or_404(
        Project.objects.filter(
            fund_id=request.user.volunteer_profile.fund_id, is_closed=False),
        pk=project_id)
    task = get_object_or_404(
        project.tasks.filter(expense__isnull=True), pk=task_id)
    expense = Expense.objects.create(
        amount=task.estimated_expense_amount, budget=budget,
        project=project, author=request.user)
    task.expense = expense
    task.save()

    return redirect(
        '%s?%s=%s' %
        (reverse('budgets:expenses_planing', args=[id]),
         'project_id', project.id))
