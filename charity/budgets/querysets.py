from django.db.models import DecimalField, Exists, Sum, Subquery, OuterRef, Value
from django.db.models.functions import Coalesce

from tasks.models import Expense

from .models import Budget, Income


def get_budget_with_avaliable_amounts_queryset(fund):
    approved_incomes_queryset = Income.objects.filter(approvement__is_rejected=False, budget=OuterRef('pk')) \
        .values('budget_id').annotate(income_sum=Sum('amount', default=0)).values('income_sum')

    approved_expenses_queryset = Expense.objects.filter(approvement__is_rejected=False,  budget=OuterRef('pk')) \
        .values('budget_id').annotate(expense_sum=Sum('amount', default=0)).values('expense_sum')

    return Budget.objects.filter(fund=fund).annotate(
        incomes_exist=Exists(Income.objects.filter(budget=OuterRef('pk'))),
        avaliable_income_amount=Coalesce(
            Subquery(approved_incomes_queryset), Value(0, output_field=DecimalField())),
        avaliable_expense_amount=Coalesce(Subquery(approved_expenses_queryset), Value(0, output_field=DecimalField()))) \
        .values('id', 'name', 'date_created',
                'author__id',
                'approvement__id', 
                'approvement__is_rejected',
                'approvement__author__username',
                'approvement__author__volunteer_profile__id',
                'approvement__author__volunteer_profile__cover',
                'manager__id',
                'manager__username',
                'manager__volunteer_profile__cover',
                'manager__volunteer_profile__id',
                'avaliable_income_amount', 'avaliable_expense_amount',
                'incomes_exist').all()
