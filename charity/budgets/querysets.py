from django.db.models import Sum, Subquery, OuterRef, Value, DecimalField
from django.db.models.functions import Coalesce

from tasks.models import Expense

from .models import Budget, Income


def get_budget_with_avaliable_amounts_queryset(fund):
    approved_income_queryset = Income.objects.filter(approvement__is_rejected=False, budget=OuterRef('pk')) \
        .values('budget_id').annotate(income_sum=Sum('amount', default=0)).values('income_sum')
    
    approved_expense_queryset = Expense.objects.filter(approvement__is_rejected=False,  budget=OuterRef('pk')) \
        .values('budget_id').annotate(expense_sum=Sum('amount', default=0)).values('expense_sum')
    
    return Budget.objects.filter(fund=fund).annotate(
        avaliable_income_amount=Coalesce(Subquery(approved_income_queryset), Value(0, output_field=DecimalField())),
        avaliable_expense_amount=Coalesce(Subquery(approved_expense_queryset), Value(0, output_field=DecimalField()))) \
        .values('id', 'name', 'date_created', 'approvement__id', 'approvement__is_rejected',
                'approvement__author__username',
                'approvement__author__volunteer_profile__id',
                'approvement__author__volunteer_profile__cover',
                'manager__username', 
                'manager__volunteer_profile__cover',
                'manager__volunteer_profile__id',
                'avaliable_income_amount', 'avaliable_expense_amount').all()
