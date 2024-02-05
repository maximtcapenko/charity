from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property

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
    reviewers = models.ManyToManyField(User, related_name='budget_reviewers')
    payout_excess_contribution = models.ForeignKey(
        Contribution, null=True, on_delete=models.SET_NULL)

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

    @cached_property
    def total_approved_amount(self):
        return self.incomes.filter(approvement__is_rejected=False) \
            .aggregate(approved_income=models.Sum('amount', default=0))['approved_income']

    @property
    def avaliable_income_amount(self):
        return self.total_approved_amount - self.total_approved_expenses_amount

    @cached_property
    def total_approved_expenses_amount(self):
        return self.expenses.filter(approvement__is_rejected=False) \
            .aggregate(approved_expense=models.Sum('amount', default=0))['approved_expense']


class Income(Base):
    budget = models.ForeignKey(
        Budget, on_delete=models.PROTECT, related_name='incomes')
    contribution = models.ForeignKey(Contribution, on_delete=models.PROTECT,
                                     related_name='incomes')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT)
    reviewer = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, related_name='reviewed_incomes')
    notes = models.TextField(blank=True, null=True)

    approvement = models.ForeignKey(
        Approvement, on_delete=models.SET_NULL, null=True)
    approvements = models.ManyToManyField(
        Approvement, related_name='approved_incomes')

    @property
    def is_approved(self):
        return self.approvement.is_rejected == False


def fund_active_budgets_count(self):
    return Budget.objects.filter(fund__id=self.id, is_closed=False) \
        .aggregate(total=models.Count('id'))['total']


def fund_active_budget_amount(self):
    return Income.objects.filter(
        approvement__is_rejected=False, budget__is_closed=False,
        budget__fund__id=self.id, budget__approvement__is_rejected=False) \
        .aggregate(budget=models.Sum('amount', default=0))['budget']


Fund.add_to_class('active_budget_amount', property(
    fget=fund_active_budget_amount
))


Fund.add_to_class('active_budgets_count', property(
    fget=fund_active_budgets_count))
