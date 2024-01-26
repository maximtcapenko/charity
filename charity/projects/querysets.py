from django.db.models import Count, DecimalField, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce

from tasks.models import Task

from .models import Project


def get_projects_with_tasks_queryset(fund):
    active_budget_queryset = Task.objects.filter(project=OuterRef('pk'), expense__approvement__is_rejected=False) \
        .values('project_id').annotate(budget=Sum('expense__amount', default=0)).values('budget')

    active_task_count_queryset = Task.objects.filter(
        is_done=False, is_started=True, project=OuterRef('pk')) \
        .values('project_id').annotate(active_tasks=Count('id')).values('active_tasks')

    total_task_count_queryset = Task.objects.filter(
        project=OuterRef('pk')).values('project_id') \
        .annotate(all_tasks=Count('id')).values('all_tasks')

    return Project.objects.filter(fund=fund).annotate(
        active_tasks_count=Coalesce(Subquery(active_task_count_queryset),Value(0)),
        tasks_count=Coalesce(Subquery(total_task_count_queryset), Value(0)),
        approved_budget=Coalesce(Subquery(active_budget_queryset), Value(0, output_field=DecimalField())))\
        .values('id', 'name', 'date_created',
                'leader__username',
                'approved_budget',
                'is_closed',
                'active_tasks_count',
                'tasks_count',
                'author__id',
                'leader__id',
                'leader__volunteer_profile__id',
                'leader__volunteer_profile__cover')
