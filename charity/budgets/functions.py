from django.db.models import Sum
from django.shortcuts import get_object_or_404
from .models import Budget
from tasks.models import Expense


def get_budget_available_income(budget):
    pending_expense_amount = Expense.objects.filter(
        budget_id=budget.id, approvement__isnull=True)\
        .aggregate(pending_expense_amount=Sum('amount', default=0))['pending_expense_amount']

    return budget.avaliable_income_amount - pending_expense_amount


def get_budget_or_404(request, id):
    return get_object_or_404(Budget.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id), pk=id)
