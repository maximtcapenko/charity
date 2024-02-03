from django.contrib.auth.models import User
from django.db.models import Count, Exists, Q, OuterRef, Sum

from funds. models import VolunteerProfile
from processes.models import ProcessState
from projects.models import Project
from wards.models import Ward

from .models import Task


def get_estimated_and_not_approved_tasks_queryset(project_id):
    return Task.objects.filter(project_id=project_id, expense__isnull=True).select_related('ward')


def get_project_requested_expenses_queryset(fund_id):
    """
    Returns queryset with structure:
    {'project__id', 'project__name', 'requested_budget'}
    """
    return Task.objects.filter(project__fund_id=fund_id, expense__isnull=True).values('project_id') \
        .annotate(requested_budget=Sum('estimated_expense_amount', default=0)) \
        .filter(requested_budget__gt=0).values('project__id', 'project__name', 'requested_budget')


def get_task_state_review_count_queryset(task):
    """
    Returns queryset with structure:
    `{'id', 'reviews_count'}`
    """
    return task.states \
        .annotate(reviews_count=Count('approvements')) \
        .values('id', 'reviews_count')


def get_project_tasks_comments_count_queryset(project):
    """
    Returns queryset with structure:
    `{'id', 'comments_count'}`
    """
    return Task.objects.filter(project=project) \
        .annotate(comments_count=Count('comments')) \
        .values('id', 'comments_count')


def get_task_comments_authors_queryset(task):
    return VolunteerProfile.objects.filter(
        user_id__in=task.comments.values('author_id')).all()


def get_available_project_wards_queryset(project, **kwargs):
    """
    Returns `Ward` queryset
    kwargs parameter `task_id`
    """
    task_id = kwargs.get('task_id')
    task_q = Q(ward=OuterRef("pk"), project__id=project.id)
    if task_id:
        task_q = task_q & ~Q(id=task_id)

    return Ward.active_objects. \
        filter(Q(projects__in=[project]) & ~
               Exists(Task.objects.filter(task_q)))


def get_available_task_rewiewers_queryset(task):
    """
    Returns `User` queryset
    """
    return User.objects.filter(
        ~Q(id__in=[task.assignee.id]) &
        Exists(Project.objects.filter(id=task.project_id, reviewers__id=OuterRef('pk'))))


def get_available_task_process_states_queryset(task):
    """
    Returns `ProcessState` queryset
    """
    current_state = task.state
    if current_state:
        queryset = Q(process__id=task.process_id) & ~Q(
            id=current_state.state_id)
    else:
        queryset = Q(process__id=task.process_id)

    return ProcessState.objects.filter(
        queryset & ~Exists(
            task.states.filter(
                state=OuterRef('pk'), approvement__is_rejected=False)))
