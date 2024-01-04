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
    approvements = models.ManyToManyField(
        Approvement, related_name='expense_approvements')


class TaskState(Base):
    state = models.ForeignKey(ProcessState, on_delete=models.PROTECT)
    completion_date = models.DateTimeField(null=True)
    approvement = models.ForeignKey(
        Approvement, on_delete=models.SET_NULL, null=True)
    prev_state = models.ForeignKey('self', null=True, on_delete=models.PROTECT)


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
    assignee = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='assigned_tasks')
    state = models.ForeignKey(TaskState, on_delete=models.PROTECT, null=True)
    expense = models.OneToOneField(
        Expense, on_delete=models.PROTECT, null=True, related_name='task')
    ward = models.ForeignKey(
        Ward, on_delete=models.PROTECT, null=True, related_name='tasks')
    attachments = models.ManyToManyField(Attachment)

    @property
    def next_task_state(self):
        if self.state:
            return self.state.state.next_state
        else:
            return self.process.states.filter(is_first=True, is_inactive=False).first()

    @property
    def is_approved(self):
        if self.should_be_approved:
            if self.expense and self.expense.budget.approvement_id \
                and self.expense.approvement:
                return not self.expense.approvement.is_rejected
            else:
                return False
        else:
            return True

    @property
    def should_be_approved(self):
        return self.estimated_expense_amount > 0

    @property
    def is_expired(self):
        return self.end_date is not None and self.end_date < datetime.date.today()


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
    return Task.objects.filter(project__id=self.id, is_done=False, is_started=True) \
        .aggregate(total=models.Count('id'))['total']


def project_approved_budget(self):
    return Task.objects.filter(project__id=self.id, expense__approvement__is_rejected=False) \
        .aggregate(budget=models.Sum('expense__amount', default=0))['budget']


def budget_approved_expenses(self):
    return Expense.objects.filter(budget__id=self.id, approvement__is_rejected=False)\
        .aggregate(budget=models.Sum('amount', default=0))['budget']


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
