from django.db import models
from django.contrib.auth.models import User
from commons.models import Base
from funds.models import Fund, Approvement, Contribution


class Budget(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='budgets')
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='created_budgets')
    approvement = models.ForeignKey(
        Approvement, on_delete=models.SET_NULL, null=True)
    closed_date = models.DateField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    manager = models.ForeignKey(
        User, null=True, on_delete=models.PROTECT, related_name='managed_budgets')
    approvements = models.ManyToManyField(
        Approvement, related_name='budget_approvements')

    def __str__(self):
        return self.name

    @property
    def is_approved(self):
        return True if self.approvement \
            and self.approvement.is_rejected == False else False

    @property
    def can_be_approved(self):
        return self.manager_id is not None

    @property
    def current_state(self):
        if (self.is_approved):
            return 'Approved'
        elif (self.is_closed):
            return 'Closed'
        else:
            return 'Planning'


class Income(Base):
    budget = models.ForeignKey(
        Budget, on_delete=models.PROTECT, related_name='incomes')
    contribution = models.ForeignKey(Contribution, on_delete=models.PROTECT,
                                     related_name='incomes')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT)
    approvement = models.ForeignKey(
        Approvement, on_delete=models.SET_NULL, null=True)
    approvements = models.ManyToManyField(
        Approvement, related_name='income_approvements')

    @property
    def is_approved(self):
        return self.approvement.is_rejected == False


def fund_active_budgets_count(self):
    return Budget.objects.filter(fund__id=self.id, is_closed=False) \
        .aggregate(total=models.Count('id'))['total']


def fund_available_budget_amount(self):
    return Income.objects.filter(budget__is_closed=False, budget__fund__id=self.id,
                                 budget__approvement__is_rejected=False) \
        .aggregate(budget=models.Sum('amount'))['budget']


def budget_avaliable_amount(self):
    approved_income = self.incomes.filter(budget__id=self.id, approvement__is_rejected=False) \
        .aggregate(approved_income=models.Sum('amount', default=0))['approved_income']
    approved_expense = self.expenses.filter(budget__id=self.id, approvement__is_rejected=False) \
        .aggregate(approved_expense=models.Sum('amount', default=0))['approved_expense']
    
    return approved_income - approved_expense


Fund.add_to_class('available_budget_amount', property(
    fget=fund_available_budget_amount
))


Fund.add_to_class('active_budgets_count', property(
    fget=fund_active_budgets_count))

Budget.add_to_class('avaliable_income_amount', property(
    fget=budget_avaliable_amount
))
