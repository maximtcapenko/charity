from django.db.models import Count, DecimalField, Exists, Q, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce

from processes.models import Process, ProcessState
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
        active_tasks_count=Coalesce(
            Subquery(active_task_count_queryset), Value(0)),
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


def get_project_processes_with_tasks_queryset(project):
    """
    Returns projection `{'id', 'name', 'is_inactive', 'project_tasks_count'}`
    """
    project_task_queryset = Task.objects.filter(
        project=project,
        process=OuterRef('pk')).values('process_id').annotate(tasks_count=Count('id')).values('tasks_count')
    return project.processes.annotate(project_tasks_count=Coalesce(Subquery(project_task_queryset), Value(0))) \
        .values('id', 'name', 'is_inactive', 'project_tasks_count')


def get_project_wards_with_tasks_queryset(project):
    """
    Returns projections `{'id', 'name', 'date_created', 'is_inactive', 'cover', 'project_tasks_count'}`
    """
    project_task_queryset = Task.objects.filter(
        project=project,
        ward=OuterRef('pk')).values('ward_id').annotate(tasks_count=Count('id')).values('tasks_count')

    return project.wards.annotate(project_tasks_count=Coalesce(Subquery(project_task_queryset), Value(0))) \
        .values('id', 'name', 'date_created', 'is_inactive', 'cover', 'project_tasks_count')


def get_project_rewiewers_with_tasks_queryset(project):
    """
    Returns projection `{'id', 'username', 'volunteer_profile__title', 'volunteer_profile__cover', 'project_tasks_exists'}`
    """
    project_task_queryset = project.tasks.filter(
        Q(states__approvement__author=OuterRef('pk')) | Q(state__approvement__author=OuterRef('pk')) |
        Q(reviewer__id=OuterRef('pk'))).values('id')

    return project.reviewers.annotate(project_tasks_exists=Exists(project_task_queryset)) \
        .values('id', 'username', 'volunteer_profile__title', 'volunteer_profile__cover', 'project_tasks_exists')


def get_avaliable_for_select_queryset(project):
    return Process.objects.filter(
        Exists(ProcessState.objects.filter(process=OuterRef('pk'))) &
        Q(is_inactive=False, fund=project.fund) &
        ~Q(projects__in=[project])) \
        .annotate(states_count=Count('states', distinct=True)) \
        .values('id', 'name', 'states_count')
