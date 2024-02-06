import datetime

from django.db import models
from django.contrib.auth.models import User

from comments.models import Comment
from commons.models import Base

from budgets.models import Budget
from files.models import Attachment
from funds.models import Approvement, Contribution, RequestReview
from processes.models import Process, ProcessState
from projects.models import Project
from wards.models import Ward


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
    reviewer = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, related_name='reviewed_task_states')
    is_done = models.BooleanField(default=False, null=False)
    is_review_requested = models.BooleanField(default=False, null=False)
    request_review = models.ForeignKey(
        RequestReview, on_delete=models.SET_NULL, null=True)
    comments = models.ManyToManyField(
        Comment, related_name='commented_task_states')

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
    actual_expense_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    process = models.ForeignKey(
        Process, on_delete=models.PROTECT, related_name='tasks')
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
    payout_excess_contribution = models.ForeignKey(
        Contribution, null=True, on_delete=models.SET_NULL, related_name='tasks')
    attachments = models.ManyToManyField(Attachment)
    states = models.ManyToManyField(TaskState, related_name='state_tasks')
    subscribers = models.ManyToManyField(User, related_name='subscribed_tasks')
    comments = models.ManyToManyField(Comment, related_name='commented_tasks')

    def __str__(self):
        return self.name

    @property
    def is_on_review(self):
        return self.is_started and self.state_id and self.state.is_review_requested and not self.is_done

    @property
    def should_be_approved(self):
        return self.estimated_expense_amount > 0

    @property
    def is_expired(self):
        return self.is_started and self.end_date is not None and self.end_date < datetime.date.today()


def user_assigned_active_tasks(self):
    return self.assigned_tasks.filter(is_done=False)


User.add_to_class('assigned_active_tasks', property(
    fget=user_assigned_active_tasks
))
