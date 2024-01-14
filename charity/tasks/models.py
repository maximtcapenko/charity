import datetime

from django.db import models
from django.contrib.auth.models import User
from commons.models import Base
from files.models import Attachment
from funds.models import Approvement
from budgets.models import Budget
from wards.models import Ward
from processes.models import Process, ProcessState
from projects.models import Project


class Expense(Base):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    budget = models.ForeignKey(
        Budget, on_delete=models.PROTECT, related_name='expenses')
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name='expenses')
    author = models.ForeignKey(
        User, on_delete=models.PROTECT)
    approvement = models.ForeignKey(
        Approvement, on_delete=models.SET_NULL, null=True)
    reviewer = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, related_name='reviewed_expenses')
    notes = models.TextField(blank=True, null=True)
    approvements = models.ManyToManyField(
        Approvement, related_name='approved_expenses')


class TaskState(Base):
    state = models.ForeignKey(ProcessState, on_delete=models.PROTECT)
    completion_date = models.DateTimeField(null=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    approvement = models.ForeignKey(
        Approvement, on_delete=models.SET_NULL, null=True)
    approvements = models.ManyToManyField(
        Approvement, related_name='approved_task_states')
    notes = models.TextField(blank=True, null=True)
    """
    TODO: add is_in_progress or approvement_requested flag
    so if step is in progress then it can not be approved
    """
    class Meta:
        ordering = ['date_created']

    def __str__(self):
        return self.state.name


class Task(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    order_position = models.IntegerField()
    is_high_priority = models.BooleanField()
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    is_started = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    estimated_expense_amount = models.DecimalField(
        max_digits=10, decimal_places=2)
    process = models.ForeignKey(
        Process, on_delete=models.PROTECT)
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name='tasks')
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='created_tasks')
    reviewer = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, related_name='reviewed_tasks')
    assignee = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='assigned_tasks')
    state = models.ForeignKey(TaskState, on_delete=models.PROTECT, null=True)
    expense = models.OneToOneField(
        Expense, on_delete=models.PROTECT, null=True, related_name='task')
    ward = models.ForeignKey(
        Ward, on_delete=models.PROTECT, null=True, related_name='tasks')
    attachments = models.ManyToManyField(Attachment)
    states = models.ManyToManyField(TaskState, related_name='state_tasks')
    subscribers = models.ManyToManyField(User, related_name='subscribed_tasks')

    def __str__(self):
        return self.name

    @property
    def should_be_approved(self):
        return self.estimated_expense_amount > 0

    @property
    def is_expired(self):
        return self.is_started and self.end_date is not None and self.end_date < datetime.date.today()


class Comment(Base):
    task = models.ForeignKey(
        Task, on_delete=models.PROTECT, related_name='comments')
    notes = models.TextField(blank=True, null=True)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='comments')
    reply = models.ForeignKey(
        'self', null=True, on_delete=models.SET_NULL, related_name='replies')
    '''use @user_name in comment notes in order to tag user'''
    tagged_interlocutors = models.ManyToManyField(
        User, related_name='tags')


def project_expired_tasks_count(self):
    return Task.objects.filter(models.Q(project__id=self.id, is_done=False, is_started=True) &
                               models.Q(end_date__isnull=False, end_date__lt=datetime.date.today())) \
        .aggregate(total=models.Count('id'))['total']


def project_active_tasks_count(self):
    return self.tasks.filter(is_done=False, is_started=True) \
        .aggregate(total=models.Count('id'))['total']


def project_approved_budget(self):
    return Task.objects.filter(project__id=self.id, expense__approvement__is_rejected=False) \
        .aggregate(budget=models.Sum('expense__amount', default=0))['budget']


def budget_approved_expenses(self):
    return Expense.objects.filter(budget__id=self.id, approvement__is_rejected=False)\
        .aggregate(budget=models.Sum('amount', default=0))['budget']


def user_assigned_active_tasks(self):
    return self.assigned_tasks.filter(is_done=False)


Project.add_to_class('active_tasks_count', property(
    fget=project_active_tasks_count))

Project.add_to_class('approved_budget', property(
    fget=project_approved_budget
))

Project.add_to_class('expired_tasks_count', property(
    fget=project_expired_tasks_count
))

Budget.add_to_class('avaliable_expenses_amount', property(
    fget=budget_approved_expenses
))

User.add_to_class('assigned_active_tasks', property(
    fget=user_assigned_active_tasks
))
