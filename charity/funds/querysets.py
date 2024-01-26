from django.db.models import Exists, Sum, OuterRef

from budgets.models import Income

from .models import Contribution


def get_contributor_budgets_queryset(contributor):
    return Income.objects.filter(
        contribution__contributor=contributor, approvement__is_rejected=False) \
        .values('budget_id').annotate(budget_amount=Sum('amount', default=0)) \
        .values('budget__id', 'budget__name', 'budget_amount',
                'budget__date_created', 'budget__approvement__id',
                'budget__approvement__is_rejected')


def get_contributions_queryset(fund):
    return Contribution.objects.filter(fund=fund) \
        .annotate(incomes_exist=Exists(Income.objects.filter(contribution=OuterRef('pk')))) \
        .values('id', 'author__username', 'amount', 'notes', 'contribution_date',
                'author__volunteer_profile__id',
                'author__volunteer_profile__cover',
                'contributor__id',
                'contributor__name',
                'contributor__cover',
                'incomes_exist')


def get_contribution_details_queryset(contribution):
    return contribution.incomes.filter(approvement__is_rejected=False) \
        .values('budget__date_created',
                'budget__id', 'budget__name', 'budget__approvement__id',
                'budget__approvement__is_rejected') \
        .annotate(budget_amount=Sum('amount', default=0))
