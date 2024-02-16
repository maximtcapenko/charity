import datetime

from django import forms
from django.db.models import Max

from commons.forms import user_model_choice_field
from commons.functional import should_be_approved
from commons.mixins import FormControlMixin, InitialMixin

from files.forms import CreateAttachmentForm
from funds.models import Approvement, Contribution, Contributor
from processes.models import Process

from .querysets import get_available_task_process_states_queryset, \
    get_available_task_rewiewers_queryset, get_available_project_wards_queryset
from .messages import Warnings
from .models import Task, TaskState
from .signals import review_request_created


class CreateTaskForm(
        forms.ModelForm, InitialMixin, FormControlMixin):
    __initial__ = ['project', 'author']
    field_order = ['ward', 'name', 'process']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.project.widget = forms.HiddenInput()

        self.form.assignee = user_model_choice_field(
            fund=self.project.fund, label='Assignee')

        self.form.reviewer = user_model_choice_field(
            queryset=self.project.reviewers, label='Reviewer')

        self.form.ward.queryset = get_available_project_wards_queryset(
            self.project).only('id', 'name')

        self.form.process.queryset = Process.objects \
            .filter(projects__in=[self.project]) \
            .only('id', 'name')

        FormControlMixin.__init__(self)

    def clean(self):
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']

        reviewer = self.cleaned_data['reviewer']
        assignee = self.cleaned_data['assignee']
        if reviewer == assignee:
            raise forms.ValidationError(
                Warnings.ASSIGNEE_CANNOT_BE_A_TASK_REVIEWER)

        if not self.project.reviewers.contains(reviewer):
            raise forms.ValidationError(
                Warnings.REVIEWER_IS_NOT_PROJECT_REVIEWER)

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                Warnings.END_DATE_CANNOT_BE_LESS_THAN_START_DATE)

        return self.cleaned_data

    def save(self):
        last_order_position = Task.objects.filter(project=self.instance.project) \
            .aggregate(result=Max('order_position'))['result']
        self.instance.order_position = last_order_position + 1 if last_order_position else 1
        if not self.instance.author_id:
            self.instance.author = self.author

        return super().save()

    class Meta:
        model = Task
        exclude = ['date_created', 'id', 'expense', 'state', 'comments', 'payout_excess_contribution',
                   'states', 'subscribers', 'author', 'actual_expense_amount',
                   'attachments', 'order_position', 'is_done', 'is_started']


class UpdateTaskForm(CreateTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            if self.instance.is_started:
                self.form.start_date.disabled = True

            self.form.ward.queryset = get_available_project_wards_queryset(
                self.instance.project, task_id=self.instance.id
            ).only('id', 'name')

            if self.instance.expense and \
                    should_be_approved(self.instance.expense):
                self.fields.pop('estimated_expense_amount')
                self.fields['ward'].disabled = True

            if self.instance.state_id:
                self.fields.pop('process')

    def save(self):
        if self.instance.reviewer_id \
                and not self.instance.subscribers.contains(self.instance.reviewer):
            self.instance.subscribers.add(self.instance.reviewer)

        self.instance.save()
        return self.instance


class CompleteTaskForm(forms.Form,  InitialMixin, FormControlMixin):
    __initial__ = ['task', 'author', 'fund']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        if self.task.expense:
            self.form.expense_amount = forms.DecimalField(
                disabled=True, initial=self.task.expense.amount, label='Expense amount')
            self.form.actual_expense_amount = forms.DecimalField(
                required=True, label='Actual expense amount')
            self.form.contributor = forms.ModelChoiceField(
                queryset=Contributor.objects.filter(
                    fund=self.fund, is_internal=True),
                required=False, label='Contributor')

        self.form.notes = forms.CharField(widget=forms.Textarea)

        FormControlMixin.__init__(self)

    def clean(self):
        task = self.task
        if task.expense:
            actual_expense_amount = self.cleaned_data.get(
                'actual_expense_amount')
            if not actual_expense_amount:
                raise forms.ValidationError(
                    Warnings.TASK_HAS_EXPENSES_ACUTAL_EXPENSE_AMOUNT_SHOULD_BE_INDICATED)

            contributor = self.cleaned_data.get('contributor')

            if actual_expense_amount > 0 and actual_expense_amount < task.expense.amount and not contributor:
                raise forms.ValidationError(
                    Warnings.CONTRIBUTOR_SHOULD_BE_INDICATED)

            if actual_expense_amount > task.expense.amount:
                raise forms.ValidationError(
                    Warnings.ACTUAL_EXPENSE_IS_BIGGER_TAHN_APPROVED)

            if not contributor.is_internal:
                raise forms.ValidationError(
                    Warnings.CONTRIBUTOR_SHOULD_BE_INTERNAL)

        return self.cleaned_data

    def save(self):
        self.task.is_done = True

        if self.task.expense:
            actual_expense_amount = self.cleaned_data['actual_expense_amount']
            self.task.actual_expense_amount = actual_expense_amount

            if self.task.expense.amount > actual_expense_amount:
                payout_excess_contribution = Contribution(
                    fund=self.fund, contribution_date=datetime.datetime.utcnow(),
                    author=self.author,
                    contributor=self.cleaned_data['contributor'],
                    amount=self.task.expense.amount - actual_expense_amount,
                    notes=self.cleaned_data['notes'])
                payout_excess_contribution.save()

                self.task.payout_excess_contribution = payout_excess_contribution

        self.task.save()

        return self.task


class ActivateTaskStateForm(
        forms.ModelForm, InitialMixin, FormControlMixin):
    __initial__ = ['task', 'author']

    field_order = ['state', 'reviewer', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.form.state.queryset = get_available_task_process_states_queryset(
            self.task)
        if self.initial.get('state'):
            self.form.state.disabled = True

        self.form.reviewer.queryset = get_available_task_rewiewers_queryset(
            self.task)

    def save(self):
        self.instance.author = self.author
        self.instance.save()

        if not self.task.state:
            self.task.is_started = True

        self.task.state = self.instance
        self.task.states.add(self.instance)
        self.task.save()

        return self.instance

    def clean(self):
        if self.instance.reviewer == self.task.assignee:
            raise forms.ValidationError(
                Warnings.REVIEWER_CANNOT_BE_A_TASK_ASSIGNEE)

        '''validate if budget of task is approved'''
        if self.task.should_be_approved:
            if self.task.expense == None:
                raise forms.ValidationError(
                    Warnings.TASK_IS_NOT_INCLUDED_IN_BUDGET)
            elif self.task.expense.budget.approvement == None:
                raise forms.ValidationError(
                    Warnings.TASK_IN_A_BUDGET_BUT_BUDGET_IS_NOT_APPROVED)
            elif self.task.expense.budget.approvement.is_rejected:
                raise forms.ValidationError(
                    Warnings.TASK_IN_A_BUDGET_BUT_BUDGET_IS_REJECTED)
            elif self.task.expense.approvement.is_rejected:
                raise forms.ValidationError(Warnings.TASK_EXPENSE_IS_REJECTED)

        '''validate if current state has approvement'''
        if self.task.state and not should_be_approved(self.task.state):
            raise forms.ValidationError(Warnings.CURRENT_TASK_IS_NOT_APPROVED)

        return self.cleaned_data

    class Meta:
        model = TaskState
        exclude = [
            'id', 'date_created', 'is_done', 'is_review_requested',
            'comments', 'request_review',
            'approvement', 'completion_date', 'author', 'approvements']


class ApproveTaskStateForm(
        forms.Form, InitialMixin, FormControlMixin):
    __initial__ = ['fund', 'author', 'state', 'task']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)
        FormControlMixin.__init__(self)

    is_rejected = forms.BooleanField(label='Reject', required=False)
    notes = forms.CharField(
        widget=forms.Textarea(),
        label='Notes', required=False)

    def clean(self):
        if should_be_approved(self.state):
            raise forms.ValidationError(Warnings.TASK_STATE_IS_APPROVED)

        if not self.author in [self.state.request_review.reviewer]:
            raise forms.ValidationError(
                Warnings.CURRENT_USER_IS_NOT_TASK_REVIEWER)

    def save(self):
        approvement = Approvement.objects.create(
            author=self.author, fund=self.fund,
            notes=self.cleaned_data['notes'],
            is_rejected=self.cleaned_data['is_rejected'])

        self.state.approvement = approvement
        self.state.is_review_requested = False

        if approvement.is_rejected == False:
            self.state.completion_date = datetime.datetime.utcnow()
            self.state.is_done = True

        self.state.approvements.add(approvement)
        self.state.save()

        return self.state


class TaskCreateAttachmentForm(CreateAttachmentForm, InitialMixin):
    __initial__ = ['fund', 'author', 'task']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

    def save(self):
        self.instance.author = self.author
        self.instance.fund = self.fund
        self.instance.save()

        self.task.attachments.add(self.instance)

        return self.instance


class TaskStateReviewRequestForm(
        forms.Form, InitialMixin, FormControlMixin):
    __initial__ = ['fund', 'author', 'state', 'task']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)
        FormControlMixin.__init__(self)

    notes = forms.CharField(widget=forms.Textarea(), min_length=10,
                            label='Message', required=True)

    def clean(self):
        if self.author != self.task.assignee:
            raise forms.ValidationError(
                Warnings.CURRENT_USER_IS_NOT_TASK_ASSIGNEE)

        if self.state.is_review_requested:
            raise forms.ValidationError(
                Warnings.TASK_STATE_REVIEW_REQUEST_HAS_BEEN_SENT)

        if should_be_approved(self.state):
            raise forms.ValidationError(Warnings.TASK_STATE_IS_APPROVED)

        return self.cleaned_data

    def save(self):
        self.state.is_review_requested = True
        self.state.save()

        review_request_created.send(
            sender=TaskState,
            instance=self.state,
            fund=self.fund,
            task=self.task,
            message=self.cleaned_data['notes']
        )

        return self.state
