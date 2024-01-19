from django.contrib.auth.models import User
from django.db.models import Count, Exists, Q, OuterRef

from funds. models import VolunteerProfile
from processes.models import ProcessState
from projects.models import Project
from wards.models import Ward

from .models import Task


def get_task_comments_with_reply_count_queryset(task):
    return task.comments.filter(
        reply_id__isnull=True).annotate(
        replies_count=Count('replies')).order_by('date_created')


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
