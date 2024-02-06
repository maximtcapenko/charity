from django.db.models import signals
from django.dispatch import receiver
from django.urls import reverse

from commons.models import Notification

from funds.models import Contribution, RequestReview

from .models import Task, TaskState


review_request_created = signals.Signal()


@receiver(signals.post_save, sender=Task)
def add_default_subscribers_wheb_task_added(sender, instance, created, **kwargs):
    if created:
        """When task has been created we add to default subscribers next users
        - task author
        - task assignee
        - project leader
        - task reviewer
        """
        project = instance.project
        subscribers = list(instance.subscribers.all())

        if not project.leader in subscribers:
            instance.subscribers.add(project.leader)
        if instance.assignee not in subscribers:
            instance.subscribers.add(instance.assignee)
        if not instance.author in subscribers:
            instance.subscribers.add(instance.author)
        if instance.reviewer_id and not instance.reviewer in subscribers:
            instance.subscribers.add(instance.reviewer)


@receiver(review_request_created, sender=TaskState)
def notify_reviewer_when_review_request_created(sender, instance, fund, task, message, **kwargs):
    reviewer = instance.reviewer if instance.reviewer else task.reviewer
    notification = Notification.objects.create(
        receiver=reviewer,
        title=Task.__name__,
        url=reverse('tasks:get_state_details', args=[task.id, instance.id]),
        short='Task review request',
        message=f'Review task state {instance.state.name} from {task.assignee} details: {message}')

    instance.request_review = RequestReview.objects.create(
        author=task.assignee,
        reviewer=reviewer, 
        fund=fund, 
        notes=message, 
        notification=notification)
    instance.save()


@receiver(signals.pre_delete, sender=Contribution)
def move_task_in_progress_when_linked_contribution_removed(sender, instance, **kwargs):
    tasks = Task.objects.filter(payout_excess_contribution=instance).all()
    for task in tasks:
        task.is_done = False
        task.save()