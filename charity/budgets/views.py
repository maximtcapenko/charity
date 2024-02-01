import uuid
from django.db.models import Exists, Q, OuterRef
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from commons import DEFAULT_PAGE_SIZE
from commons.exceptions import ApplicationError
from commons.functions import user_should_be_volunteer, render_generic_form, \
    should_be_approved, wrap_dict_set_to_objects_list, wrap_dicts_page_to_objects_page
from funds.models import Approvement
from projects.models import Project
from tasks.querysets import get_estimated_and_not_approved_tasks_queryset, \
    get_project_requested_expenses_queryset
from tasks.models import Task, Expense

from .forms import CreateBudgetForm, CreateIncomeForm, \
    BudgetItemApproveForm, ApproveBudgetForm, UpdateBudgetForm, \
    AddBudgetReviewerForm, CreateExpenseForm, EditBudgetItemForm

from .querysets import get_budget_with_avaliable_amounts_queryset
from .functions import get_budget_or_404, get_budget_available_income, validate_pre_requirements
from .messages import Warnings
from .models import Budget, Income


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def create(request):
    return render_generic_form(
        request=request, form_class=CreateBudgetForm,
        context={
            'return_url': reverse("budgets:get_list"),
            'title': 'Add budget',
            'initial': {
                'fund': request.user.volunteer_profile.fund,
                'author': request.user,
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_details(request, id):
    budget = get_budget_or_404(request, id)
    return_url = reverse('budgets:get_details', args=[id])

    validate_pre_requirements(request, budget, return_url)

    return render_generic_form(
        request=request, form_class=UpdateBudgetForm,
        context={
            'return_url': return_url,
            'title': 'Edit budget',
            'initial': {
                'fund': request.user.volunteer_profile.fund,
                'author': request.user,
            },
            'instance': budget
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def approve_budget(request, id):
    budget = get_budget_or_404(request, id)
    return_url = f'{reverse("budgets:get_details", args=[id])}?tab=approvements'

    validate_pre_requirements(request, budget, return_url)

    return render_generic_form(
        request=request,
        form_class=ApproveBudgetForm, context={
            'return_url': return_url,
            'title': 'Add approvement',
            'initial': {
                'author': request.user,
                'fund': request.user.volunteer_profile.fund,
                'target': budget
            },
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_budget(request, id):
    budget = get_budget_or_404(request, id)
    return_url = reverse('budgets:get_list')

    validate_pre_requirements(request, budget, return_url)
    if budget.incomes.exists():
        raise ApplicationError(
            Warnings.BUDGET_CANNOT_BE_DELETED_IT_HAS_INCOMES, return_url)

    budget.delete()
    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_budget_income(request, id):
    return_url = reverse('budgets:get_details', args=[id])
    budget = get_budget_or_404(request, id)

    validate_pre_requirements(request, budget, return_url)

    return render_generic_form(
        request=request, form_class=CreateIncomeForm,
        context={
            'return_url': return_url,
            'title': 'Add income',
            'initial': {
                'author': request.user,
                'budget': budget
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_budget_income_details(request, id, income_id):
    budget = get_budget_or_404(request, id)
    income = get_object_or_404(budget.incomes, pk=income_id)
    return_url = reverse('budgets:get_income_details',
                         args=[budget.id, income_id])

    validate_pre_requirements(request, income, return_url)

    return render_generic_form(
        request=request, form_class=EditBudgetItemForm, context={
            'return_url': return_url,
            'title': 'Edit budget income',
            'initial': {
                'budget': budget,
                'target': income
            }
        }
    )


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def approve_budget_income(request, id, income_id):
    budget = get_budget_or_404(request, id)
    income = get_object_or_404(budget.incomes, pk=income_id)
    return_url = reverse('budgets:get_income_details',
                         args=[budget.id, income_id])

    validate_pre_requirements(request, income, return_url, action='approve')

    return render_generic_form(
        request=request,
        form_class=BudgetItemApproveForm, context={
            'return_url': return_url,
            'title': 'Add approvement',
            'initial': {
                'author': request.user,
                'fund': request.user.volunteer_profile.fund,
                'target': income
            },
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_budget_income(request, id, income_id):
    budget = get_budget_or_404(request, id)
    return_url = f'{reverse("budgets:get_details", args=[id])}?tab=incomes'

    validate_pre_requirements(request, budget, return_url)

    if should_be_approved(budget):
        raise ApplicationError(
            Warnings.INCOME_CANNOT_BE_DELETED_BUDGET_APPROVED, return_url)

    income = get_object_or_404(budget.incomes, pk=income_id)

    if should_be_approved(income):
        raise ApplicationError(
            Warnings.INCOME_CANNOT_BE_DELETED_IT_HAS_BEEN_APPROVED, return_url)

    income.delete()
    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_budget_expense(request, id):
    budget = get_budget_or_404(request, id)
    project_id = request.GET.get('project_id')
    task_id = request.GET.get('task_id')
    return_url = '%s?%s=%s' % (reverse('budgets:expenses_planing', args=[
                               budget.id]), 'project_id', project_id)

    validate_pre_requirements(request, budget, return_url)

    project = get_object_or_404(
        Project.objects.filter(
            fund_id=request.user.volunteer_profile.fund_id,
            is_closed=False),
        pk=project_id)
    task = get_object_or_404(project.tasks.filter(
        expense__isnull=True), pk=task_id)

    return render_generic_form(
        request=request, form_class=CreateExpenseForm,
        context={
            'return_url': return_url,
            'title': 'Add expense',
            'initial': {
                'author': request.user,
                'budget': budget,
                'project': project,
                'task': task
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_budget_expense_details(request, id, expense_id):
    budget = get_budget_or_404(request, id)
    expense = get_object_or_404(budget.expenses, pk=expense_id)
    return_url = reverse('budgets:get_expense_details',
                         args=[budget.id, expense_id])

    validate_pre_requirements(request, expense, return_url)

    return render_generic_form(
        request=request, form_class=EditBudgetItemForm, context={
            'return_url': return_url,
            'title': 'Edit budget expense',
            'initial': {
                'budget': budget,
                'target': expense
            }
        }
    )


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def approve_budget_expense(request, id, expense_id):
    budget = get_budget_or_404(request, id)
    expense = get_object_or_404(budget.expenses, pk=expense_id)
    return_url = reverse('budgets:get_expense_details',
                         args=[budget.id, expense_id])

    validate_pre_requirements(request, expense, return_url, action='approve')

    return render_generic_form(
        request=request,
        form_class=BudgetItemApproveForm, context={
            'return_url': return_url,
            'title': 'Add approvement',
            'initial': {
                'author': request.user,
                'fund': request.user.volunteer_profile.fund,
                'target': expense
            },
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_budget_expense(request, id, expense_id):
    budget = get_budget_or_404(request, id)
    return_url = f'{reverse("budgets:get_details", args=[id])}?tab=expenses'

    validate_pre_requirements(request, budget, return_url)

    if should_be_approved(budget):
        raise ApplicationError(
            Warnings.EXPENSE_CANNOT_BE_DELETED_BUDGET_APPROVED, return_url)

    expense = get_object_or_404(budget.expenses, pk=expense_id)

    if should_be_approved(expense):
        raise ApplicationError(
            Warnings.EXPENSE_CANNOT_BE_DELETED_IT_HAS_BEEN_APPROVED, return_url)

    task = expense.task
    task.expense = None
    task.save()
    expense.delete()

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_budget_reviewer(request, id):
    budget = get_budget_or_404(request, id)
    return_url = f'{reverse("budgets:get_details", args=[id])}?tab=reviewers'

    validate_pre_requirements(request, budget, return_url)

    return render_generic_form(
        request=request, form_class=AddBudgetReviewerForm, context={
            'return_url': return_url,
            'title': 'Add budget reviewer',
            'initial': {
                'budget': budget
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_budget_reviewer(request, id, reviewer_id):
    budget = get_budget_or_404(request, id)
    return_url = f'{reverse("budgets:get_details", args=[id])}?tab=reviewers'

    validate_pre_requirements(request, budget, return_url)

    if budget.reviewers.count() == 1:
        """redirect to error page with return url"""
        raise ApplicationError(
            Warnings.BUDGET_REVIEWER_MUST_EXISTS, return_url)
    elif budget.manager_id == reviewer_id:
        raise ApplicationError(
            Warnings.BUDGET_REVIEWER_IS_A_MANAGER, return_url)
    elif budget.approvements.filter(author__id=reviewer_id).exists():
        raise ApplicationError(
            Warnings.BUDGET_REVIEWER_CANNOT_BE_REMOVED_REVIEWS_EXISTS, return_url)
    elif budget.incomes.filter(Q(reviewer_id=reviewer_id) | Q(approvement__author__id=reviewer_id)).exists():
        raise ApplicationError(
            Warnings.BUDGET_REVIEWER_CANNOT_BE_REMOVED_INCOMES_REVIEWS_EXISTS, return_url)
    elif budget.expenses.filter(Q(reviewer_id=reviewer_id) | Q(approvement__author__id=reviewer_id)).exists():
        raise ApplicationError(
            Warnings.BUDGET_REVIEWER_CANNOT_BE_REMOVED_EXPENSES_REVIEWS_EXISTS, return_url)

    reviewer = get_object_or_404(budget.reviewers, pk=reviewer_id)
    budget.reviewers.remove(reviewer)

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_income_details(request, id, income_id):
    budget = get_budget_or_404(request, id)
    income = get_object_or_404(budget.incomes, pk=income_id)
    paginator = Paginator(income.approvements.all(), DEFAULT_PAGE_SIZE)

    return render(request, 'budget_income_details.html', {
        'title': 'Income',
        'income': income,
        'budget': budget,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_expense_details(request, id, expense_id):
    budget = get_budget_or_404(request, id)
    expense = get_object_or_404(budget.expenses, pk=expense_id)

    paginator = Paginator(expense.approvements.all(), DEFAULT_PAGE_SIZE)

    return render(request, 'budget_expense_details.html', {
        'title': 'Expense',
        'budget': budget,
        'expense': expense,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_list(request):
    queryset = get_budget_with_avaliable_amounts_queryset(
        request.user.volunteer_profile.fund)

    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)
    page = wrap_dicts_page_to_objects_page(
        paginator.get_page(request.GET.get('page')), model=Budget)

    return render(request, 'budgets_list.html', {
        'page': page
    })


@user_passes_test(user_should_be_volunteer)
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

    budget = get_budget_or_404(request, id)
    total_approved_amount = budget.total_approved_amount
    total_approved_expenses_amount = budget.total_approved_expenses_amount

    queryset = tabs.get(tab)(budget)
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    return render(request, 'budget_details.html', {
        'title': 'Budget',
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
@require_http_methods(['GET'])
def budget_expenses_planing(request, id):
    budget = get_budget_or_404(request, id)
    if should_be_approved(budget):
        return redirect('%s?%s' % (reverse('budgets:get_details', args=[id]), 'tab=expenses'))

    avaliable_income_amount = get_budget_available_income(budget)

    results = wrap_dict_set_to_objects_list(
        get_project_requested_expenses_queryset(budget.fund_id))
    tasks = []
    selected_project = request.GET.get('project_id')
    if selected_project and len(results) > 0:
        result = next(filter(lambda result: result.project.id == uuid.UUID(
            selected_project), results), None)
        if result:
            tasks = get_estimated_and_not_approved_tasks_queryset(
                result.project.id)
    else:
        selected_project = None

    return render(request, 'budget_expenses_planing.html', {
        'title': 'Expense planing',
        'budget': budget,
        'avaliable_income_amount': avaliable_income_amount,
        'projects': results,
        'selected_project': selected_project,
        'tasks': tasks
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_reviewer_details(request, id, reviewer_id):
    default_tab = 'incomes'
    tabs = {
        'incomes': lambda budget, reviewer:
            Income.objects.filter(Q(budget=budget) & Exists(Approvement.objects.filter(
                approved_incomes=OuterRef('pk'), author=reviewer)))
        .prefetch_related('approvements'),
        'expenses': lambda budget, reviewer:
            Expense.objects.filter(Q(budget=budget) & Exists(Approvement.objects.filter(
                approved_expenses=OuterRef('pk'), author=reviewer)))
        .prefetch_related('approvements'),
    }

    tab = request.GET.get('tab', default_tab)
    if not tab in tabs:
        tab = default_tab

    budget = get_budget_or_404(request, id)
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
