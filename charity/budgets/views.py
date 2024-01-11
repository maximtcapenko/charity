import uuid
from django.db.models import Exists, Q, OuterRef, Sum
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.exceptions import ApplicationError
from commons.functions import user_should_be_volunteer, render_generic_form
from funds.models import Approvement
from .models import Budget, Income
from .forms import CreateBudgetForm, CreateIncomeForm, \
    BudgetItemApproveForm, ApproveBudgetForm, UpdateBudgetForm, AddBudgetReviewerForm
from projects.models import Project
from tasks.models import Task, Expense


def _get_budget_or_404(request, id):
    return get_object_or_404(Budget.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    return render_generic_form(
        request=request, form_class=CreateBudgetForm,
        context={
            'return_url': f'{reverse("funds:get_current_details")}?tab=budgets',
            'title': 'Add budget',
            'post_form_initial': {
                'fund': request.user.volunteer_profile.fund,
                'user': request.user,
            },
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            }
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def edit_details(request, id):
    budget = _get_budget_or_404(request, id)
    return render_generic_form(
        request=request, form_class=UpdateBudgetForm,
        context={
            'return_url': reverse('budgets:get_details', args=[id]),
            'title': 'Edit budget',
            'post_form_initial': {
                'fund': request.user.volunteer_profile.fund,
                'user': request.user,
            },
            'get_form_initial': {
                'fund': request.user.volunteer_profile.fund
            },
            'instance': budget
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
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


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def approve_budget(request, id):
    return render_generic_form(
        request=request,
        form_class=ApproveBudgetForm, context={
            'return_url': f'{reverse("budgets:get_details", args=[id])}?tab=approvements',
            'title': 'Add approvement',
            'post_form_initial': {
                'user': request.user,
                'fund': request.user.volunteer_profile.fund,
                'target': _get_budget_or_404(request, id)
            },
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def approve_budget_income(request, income_id):
    return render_generic_form(
        request=request,
        form_class=BudgetItemApproveForm, context={
            'return_url': reverse('budgets:get_income_details', args=[income_id]),
            'title': 'Add approvement',
            'post_form_initial': {
                'user': request.user,
                'fund': request.user.volunteer_profile.fund,
                'target': get_object_or_404(Income.objects.filter(
                    budget__fund__id=request.user.volunteer_profile.fund_id), pk=income_id)
            },
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def approve_budget_expense(request, expense_id):
    return render_generic_form(
        request=request,
        form_class=BudgetItemApproveForm, context={
            'return_url': reverse('budgets:get_expense_details', args=[expense_id]),
            'title': 'Add approvement',
            'post_form_initial': {
                'user': request.user,
                'fund': request.user.volunteer_profile.fund,
                'target': get_object_or_404(Expense.objects.filter(
                    budget__fund__id=request.user.volunteer_profile.fund_id), pk=expense_id)
            },
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET', 'POST'])
def add_budget_reviewer(request, id):
    initial = {
        'budget': _get_budget_or_404(request, id)
    }
    return render_generic_form(
        request=request, form_class=AddBudgetReviewerForm, context={
            'return_url': f'{reverse("budgets:get_details", args=[id])}?tab=reviewers',
            'title': 'Add budget reviewer',
            'get_form_initial': initial,
            'post_form_initial': initial
        })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def remove_budget_reviewer(request, id, reviewer_id):
    budget = _get_budget_or_404(request, id)
    return_url = f'{reverse("budgets:get_details", args=[id])}?tab=reviewers'
    if budget.reviewers.count() == 1:
        """redirect to error page with return url"""
        raise ApplicationError(
            'Budget must have at least one reviewer', return_url)

    if budget.approvements.filter(author__id=reviewer_id).exists():
        raise ApplicationError(
            'Reviewer can not be removed from budget because of reviewed approvements of budget',
            return_url
        )

    if budget.incomes.filter(approvement__author__id=reviewer_id).exists():
        raise ApplicationError(
            'Reviewer can not be removed from budget because of reviewed incomes in budget',
            return_url)

    if budget.expenses.filter(approvement__author__id=reviewer_id).exists():
        raise ApplicationError(
            'Reviewer can not be removed from budget because of reviewed expenses in budget',
            return_url)

    reviewer = get_object_or_404(budget.reviewers, pk=reviewer_id)
    budget.reviewers.remove(reviewer)

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_income_details(request, income_id):
    income = get_object_or_404(Income.objects.filter(
        budget__fund__id=request.user.volunteer_profile.fund_id), pk=income_id)

    paginator = Paginator(income.approvements.all(), DEFAULT_PAGE_SIZE)

    return render(request, 'budget_income_details.html', {
        'income': income,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_expense_details(request, expense_id):
    expense = get_object_or_404(Expense.objects.filter(
        budget__fund__id=request.user.volunteer_profile.fund_id), pk=expense_id)

    paginator = Paginator(expense.approvements.all(), DEFAULT_PAGE_SIZE)

    return render(request, 'budget_expense_details.html', {
        'expense': expense,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_list(request):
    paginator = Paginator(Budget.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), DEFAULT_PAGE_SIZE)
    return render(request, 'budgets_list.html', {
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_details(request, id):
    default_tab = 'incomes'
    tabs = {
        'incomes': lambda budget:
            budget.incomes.select_related(
                'author', 'author__volunteer_profile', 'approvement'),
        'expenses': lambda budget:
            budget.expenses.select_related(
                'author', 'approvement', 'project'),
        'approvements': lambda budget: budget.approvements.all(),
        'reviewers': lambda budget: budget.reviewers.select_related('volunteer_profile')
    }

    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab

    budget = _get_budget_or_404(request, id)
    total_approved_amount = budget.total_approved_amount
    total_approved_expenses_amount = budget.total_approved_expenses_amount

    queryset = tabs.get(tab)(budget)
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    return render(request, 'budget_details.html', {
        'tabs': tabs.keys(),
        'items_count': paginator.count,
        'budget': budget,
        'total_approved_amount': total_approved_amount,
        'total_approved_expenses_amount': total_approved_expenses_amount,
        'total_avaliable_amount': total_approved_amount-total_approved_expenses_amount,
        'selected_tab': tab,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def budget_expenses_planing(request, id):
    budget = _get_budget_or_404(request, id)
    if budget.approvement and budget.approvement.is_rejected == False:
        return redirect('%s?%s' % (reverse('budgets:get_details', args=[id]), 'tab=expenses'))

    pending_expense_amount = Expense.objects.filter(
        budget_id=budget.id, approvement__isnull=True)\
        .aggregate(pending_expense_amount=Sum('amount', default=0))['pending_expense_amount']

    avaliable_income_amount = budget.avaliable_income_amount - pending_expense_amount

    projects = Project.objects.annotate(
        requested_budget=Sum('tasks__estimated_expense_amount',
                             filter=Q(tasks__expense__isnull=True), distinct=True, default=0))\
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


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
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


@user_passes_test(user_should_be_volunteer)
@login_required
@require_http_methods(['GET'])
def get_reviewer_details(request, id, reviewer_id):
    default_tab = 'incomes'
    tabs = {
        'incomes': lambda budget, reviewer:
            Income.objects.filter(
                Q(budget=budget) &
                Exists(Approvement.objects.filter(approved_incomes=OuterRef('pk'), author=reviewer)))
        .prefetch_related('approvements'),
        'expenses': lambda budget, reviewer:
            Expense.objects.filter(
                Q(budget=budget) &
                Exists(Approvement.objects.filter(approved_expenses=OuterRef('pk'), author=reviewer)))
        .prefetch_related('approvements'),
    }

    tab = request.GET.get('tab', default_tab)

    if not tab in tabs:
        tab = default_tab
    budget = _get_budget_or_404(request, id)
    reviewer = get_object_or_404(budget.reviewers, pk=reviewer_id)

    queryset = tabs.get(tab)(budget, reviewer)
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    return render(request, 'budget_reviewer_details.html', {
        'tabs': tabs.keys(),
        'items_count': paginator.count,
        'selected_tab': tab,
        'budget': budget,
        'reviewer': reviewer,
        'page': paginator.get_page(request.GET.get('page'))
    })
