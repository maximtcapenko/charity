from django.db.models import signals
from django.dispatch import receiver
from django.urls import reverse
from commons.models import Notification

from tasks.models import Expense
from .models import Budget, Income

exprense_created = signals.Signal()


@receiver(signals.post_save, sender=Budget)
def add_default_reviewers(sender, instance, **kwargs):
    manager = instance.manager
    if not instance.reviewers.contains(manager):
        instance.reviewers.add(instance.manager)

        """Send notification to manager"""
        Notification.objects.create(
            title=Budget.__name__,
            receiver=instance.manager,
            short='Role assignment',
            message=f"You've been assigned to role Manager of budget '{instance.name}'",
            url=reverse('budgets:get_details', args=[instance.id]))


@receiver(signals.post_save, sender=Income)
def budget_income_added(sender, instance, created, **kwargs):
    if created:
        budget = instance.budget
        message = f'New income with amount {instance.amount} to budget {budget.name} has been received'
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
                short=f'New Income ({instance.amount})',
                receiver=receiver,
                message=message,
                url=reverse('budgets:get_income_details', args=[instance.id]))


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
            message = f"Income with amount {instance.amount} of budget \
              {budget.name} has been {'Rejected' if instance.approvement.is_rejected else 'Approved' }"
            Notification.objects.create(
                title=Budget.__name__,
                short=f'Income ({instance.amount}) reviewed',
                receiver=receiver,
                message=message,
                url=reverse('budgets:get_income_details', args=[instance.id]))


@receiver(exprense_created, sender=Expense)
def budget_expense_added(sender, instance, **kwargs):
    budget = instance.budget
    message = f'New expense with amount {instance.amount} to budget {budget.name} has been received'
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
            short=f'New Expense ({instance.amount})',
            receiver=receiver,
            message=message,
            url=reverse('budgets:get_expense_details', args=[instance.id]))


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

        message = f"Expense with amount {instance.amount} of budget {budget.name} \
            has been {'Rejected' if instance.approvement.is_rejected else 'Approved' }"

        for receiver in set(list(budget.reviewers.all()) + list(instance.task.subscribers.all())):
            Notification.objects.create(
                title=Budget.__name__,
                receiver=receiver,
                short=f'Exoense ({instance.amount}) reviewed',
                message=message,
                url=reverse('budgets:get_expense_details', args=[instance.id]))
