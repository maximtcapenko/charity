from django.db.models import signals
from django.dispatch import receiver
from django.urls import reverse

from commons.models import Notification

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
def notify_reviewer_when_review_request_created(sender, instance, task, message, **kwargs):
    Notification.objects.create(
        receiver=task.reviewer,
        title=Task.__name__,
        url=reverse('tasks:get_state_details', args=[task.id, instance.id]),
        short='Task review request',
        message=f'Review task state {instance.state.name} from {task.assignee} details: {message}')