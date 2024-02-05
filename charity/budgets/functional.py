from django.db.models import Sum
from django.shortcuts import get_object_or_404

from commons.exceptions import ApplicationError
from tasks.models import Expense

from .requirements import user_should_be_budget_owner, \
    user_should_be_budget_item_editor, user_should_be_budget_item_reviewer
from .models import Budget, Income
from .messages import Warnings


def get_budget_available_income(budget):
    pending_expense_amount = Expense.objects.filter(
        budget_id=budget.id, approvement__isnull=True)\
        .aggregate(pending_expense_amount=Sum('amount', default=0))['pending_expense_amount']

    return budget.avaliable_income_amount - pending_expense_amount


def get_budget_or_404(request, id):
    return get_object_or_404(Budget.objects.filter(
        fund=request.user.fund), pk=id)


def validate_pre_requirements(request, instance, return_url, action=None):
    user = request.user
    should_raise_an_error = False

    if isinstance(instance, Budget):
        should_raise_an_error = not user_should_be_budget_owner(user, instance)

    elif isinstance(instance, Income) or isinstance(instance, Expense):
        if action == 'approve':
            should_raise_an_error = not user_should_be_budget_item_reviewer(user, instance)
        else:    
            should_raise_an_error = not user_should_be_budget_item_editor(user, instance)
            
    if should_raise_an_error:
        raise ApplicationError(
                Warnings.CURRENT_USER_IS_NOT_PERMITTED, return_url)