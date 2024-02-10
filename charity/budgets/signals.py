from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.dispatch import receiver
from django.urls import reverse

from commons.models import Notification

from tasks.models import Expense

from .messages import Infos
from .models import Budget, Income

exprense_created = signals.Signal()
budget_item_reviewer_assigned = signals.Signal()


@receiver(signals.post_save, sender=Budget)
def add_default_reviewers(sender, instance, **kwargs):
    manager = instance.manager
    if not instance.reviewers.contains(manager):
        instance.reviewers.add(instance.manager)

        """Send notification to manager"""
        Notification.objects.create(
            title=Budget.__name__,
            receiver=instance.manager,
            target_content_type=ContentType.objects.get_for_model(sender),
            target_id=instance.id,
            short=Infos.NEW_ROLE_ASSIGNMENT_SHORT,
            message=Infos.NEW_ROLE_ASSIGNMENT_LONG % instance.name,
            url=reverse('budgets:get_details', args=[instance.id]))


@receiver(signals.post_delete, sender=Budget)
def clean_budget_notifications(sender, instance, **kwargs):
    notifications = Notification.objects.filter(
        target_id=instance.id,
        target_content_type=ContentType.objects.get_for_model(sender)).all()

    for notification in notifications:
        notification.delete()


@receiver(signals.post_save, sender=Income)
def budget_income_added(sender, instance, created, **kwargs):
    if created:
        budget = instance.budget
        """
        Send notification to: 
        - income reviewer
        - budget manager
        """
        receivers = [budget.manager]
        if instance.reviewer_id:
            receivers.append(instance.reviewer)

        for receiver in receivers:
            Notification.objects.create(
                title=Budget.__name__,
                short=Infos.NEW_INCOME_SHORT % f'{instance.amount:,.2f}',
                target_content_type=ContentType.objects.get_for_model(sender),
                target_id=instance.id,
                receiver=receiver,
                message=Infos.NEW_INCOME_LONG % (
                    f'{instance.amount:,.2f}', budget.name),
                url=reverse('budgets:get_income_details', args=[budget.id, instance.id]))


@receiver(signals.post_delete, sender=Income)
def clean_income_notifications(sender, instance, **kwargs):
    notifications = Notification.objects.filter(
        target_id=instance.id,
        target_content_type=ContentType.objects.get_for_model(sender)).all()

    for notification in notifications:
        notification.delete()


@receiver(signals.m2m_changed, sender=Income.approvements.through)
def budget_income_approved(sender, instance, action, **kwargs):
    if action == 'post_add':
        budget = instance.budget
        """
        Send notification to:
        - budget manager
        - income author
        """
        if not instance.approvement_id:
            return

        for receiver in [budget.manager, instance.author]:
            message = Infos.INCOME_HAS_BEEN_REVIEWED_LONG % (
                f'{instance.amount:,.2f}',
                budget.name, 'Rejected' if instance.approvement.is_rejected else 'Approved')
            Notification.objects.create(
                title=Budget.__name__,
                short=Infos.INCOME_HAS_BEEN_REVIEWED_SHORT % f'{instance.amount:,.2f}',
                target_content_type=ContentType.objects.get_for_model(Income),
                target_id=instance.id,
                receiver=receiver,
                message=message,
                url=reverse('budgets:get_income_details', args=[budget.id, instance.id]))


@receiver(exprense_created, sender=Expense)
def budget_expense_added(sender, instance, **kwargs):
    budget = instance.budget
    """
    Send notification to:
    - budget manager
    - expense reviewer
    - related task subscribers
    """
    receivers = [budget.manager]
    if instance.reviewer_id:
        receivers.append(instance.reviewer)

    receivers += list(instance.task.subscribers.all())

    for receiver in set(receivers):
        Notification.objects.create(
            title=Budget.__name__,
            short=Infos.NEW_EXPENSE_SHORT % f'{instance.amount:,.2f}',
            target_content_type=ContentType.objects.get_for_model(sender),
            target_id=instance.id,
            receiver=receiver,
            message=Infos.NEW_EXPENSE_LONG % (
                f'{instance.amount:,.2f}', budget.name),
            url=reverse('budgets:get_expense_details', args=[budget.id, instance.id]))


@receiver(signals.post_delete, sender=Expense)
def clean_expense_notifications(sender, instance, **kwargs):
    notifications = Notification.objects.filter(
        target_id=instance.id,
        target_content_type=ContentType.objects.get_for_model(sender)).all()

    for notification in notifications:
        notification.delete()


@receiver(signals.m2m_changed, sender=Expense.approvements.through)
def budget_expense_approved(sender, instance, action, **kwargs):
    if action == 'post_add':
        budget = instance.budget
        if not instance.approvement_id:
            return
        """
        Send notification to:
        - budget manager
        - expense reviewer
        - related task subscribers
        """
        receivers = [budget.manager]
        if instance.reviewer_id:
            receivers.append(instance.reviewer)

        receivers += list(instance.task.subscribers.all())

        message = Infos.EXPENSE_HAS_BEEN_REVIEWED_LONG % (
            f'{instance.amount:,.2f}',
            budget.name, 'Rejected' if instance.approvement.is_rejected else 'Approved')

        for receiver in set(list(budget.reviewers.all()) + list(instance.task.subscribers.all())):
            Notification.objects.create(
                title=Budget.__name__,
                receiver=receiver,
                target_content_type=ContentType.objects.get_for_model(Expense),
                target_id=instance.id,
                short=Infos.EXPENSE_HAS_BEEN_REVIEWED_SHORT % f'{instance.amount:,.2f}',
                message=message,
                url=reverse('budgets:get_expense_details', args=[budget.id, instance.id]))


@receiver(budget_item_reviewer_assigned)
def budget_income_reviewer_assigned(sender, budget, reviewer, instance, **kwargs):
    Notification.objects.create(
        title=Budget.__name__,
        receiver=reviewer,
        target_content_type=ContentType.objects.get_for_model(sender),
        target_id=instance.id,
        short='Review assignment',
        message=f"You've been assigned to role {sender.__name__} Reviewer'",
        url=reverse(f'budgets:get_{sender.__name__.lower()}_details', args=[budget.id, instance.id]))
