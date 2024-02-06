import datetime

from django import forms
from django.db.models import Max
from django.contrib.auth.models import User

from commons.forms import CustomLabeledModelChoiceField
from commons.functional import should_be_approved, get_reviewer_label
from commons.mixins import FormControlMixin, InitialValidationMixin

from files.forms import CreateAttachmentForm
from funds.models import Approvement, Contribution, Contributor
from processes.models import Process

from .querysets import get_available_task_process_states_queryset, \
    get_available_task_rewiewers_queryset, get_available_project_wards_queryset
from .messages import Warnings
from .models import Task, TaskState
from .signals import review_request_created


class CreateTaskForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['project', 'author']
    field_order = ['ward', 'name', 'process']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)

        self.fields['project'].widget = forms.HiddenInput()

        project = self.initial['project']
        self.fields['assignee'] = CustomLabeledModelChoiceField(
            lable_func=get_reviewer_label,
            queryset=User.objects
            .filter(volunteer_profile__fund_id=project.fund_id),
            label='Assignee', required=True)

        self.fields['reviewer'] = CustomLabeledModelChoiceField(
            lable_func=get_reviewer_label,
            queryset=project.reviewers, label='Reviewer', required=True)

        self.fields['ward'].queryset = get_available_project_wards_queryset(
            project).only('id', 'name')

        self.fields['process'].queryset = Process.objects \
            .filter(projects__in=[project]) \
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

        if not self.initial['project'].reviewers.contains(reviewer):
            raise forms.ValidationError(
                Warnings.REVIEWER_IS_NOT_PROJECT_REVIEWER)

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                Warnings.END_DATE_CANNOT_BE_LESS_THAN_START_DATE)

        return self.cleaned_data

    def save(self):
        last_order_position = Task.objects.filter(project__id=self.instance.project_id) \
            .aggregate(result=Max('order_position'))['result']
        self.instance.order_position = last_order_position + 1 if last_order_position else 1
        if not self.instance.author_id:
            self.instance.author = self.initial['author']

        return super().save()

    class Meta:
        model = Task
        exclude = ['date_created', 'id', 'expense', 'state', 'comments',
                   'states', 'subscribers', 'author', 'actual_expense_amount',
                   'attachments', 'order_position', 'is_done', 'is_started']


class UpdateTaskForm(CreateTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            if self.instance.is_started:
                self.fields['start_date'].disabled = True

            self.fields['ward'].queryset = get_available_project_wards_queryset(
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


class CompleteTaskForm(forms.Form,  InitialValidationMixin, FormControlMixin):
    __initial__ = ['task', 'author', 'fund']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)

        task = self.initial['task']
        fund = self.initial['fund']

        if task.expense:
            self.fields['expense_amount'] = forms.DecimalField(
                disabled=True, initial=task.expense.amount, label='Expense amount')
            self.fields['actual_expense_amount'] = forms.DecimalField(
                required=True, label='Actual expense amount')
            self.fields['contributor'] = forms.ModelChoiceField(
                queryset=Contributor.objects.filter(
                    fund=fund, is_internal=True),
                required=False, label='Contributor')

        self.fields['notes'] = forms.CharField(widget=forms.Textarea)

        FormControlMixin.__init__(self)

    def clean(self):
        task = self.initial['task']
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
        task = self.initial['task']
        fund = self.initial['fund']
        author = self.initial['author']

        task.is_done = True
        task.is_started = False

        if task.expense:
            actual_expense_amount = self.cleaned_data['actual_expense_amount']
            task.actual_expense_amount = actual_expense_amount

            if task.expense.amount > actual_expense_amount:
                payout_excess_contribution = Contribution(
                    fund=fund, contribution_date=datetime.datetime.utcnow(),
                    author=author,
                    contributor=self.cleaned_data['contributor'],
                    amount=actual_expense_amount,
                    notes=self.cleaned_data['notes'])
                payout_excess_contribution.save()

                task.payout_excess_contribution = payout_excess_contribution

        task.save()

        return task


class ActivateTaskStateForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['task', 'author']

    field_order = ['state', 'reviewer', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        task = self.initial['task']

        self.fields['state'].queryset = get_available_task_process_states_queryset(
            task)
        if self.initial.get('state'):
            self.fields['state'].disabled = True

        self.fields['reviewer'].queryset = get_available_task_rewiewers_queryset(
            task)

    def save(self):
        author = self.initial['author']
        task = self.initial['task']
        self.instance.author = author
        self.instance.save()

        if not task.state:
            task.is_started = True

        task.state = self.instance
        task.states.add(self.instance)
        task.save()

        return self.instance

    def clean(self):
        task = self.initial['task']
        if self.instance.reviewer == task.assignee:
            raise forms.ValidationError(
                Warnings.REVIEWER_CANNOT_BE_A_TASK_ASSIGNEE)

        '''validate if budget of task is approved'''
        if task.should_be_approved:
            if task.expense == None:
                raise forms.ValidationError(
                    Warnings.TASK_IS_NOT_INCLUDED_IN_BUDGET)
            elif task.expense.budget.approvement == None:
                raise forms.ValidationError(
                    Warnings.TASK_IN_A_BUDGET_BUT_BUDGET_IS_NOT_APPROVED)
            elif task.expense.budget.approvement.is_rejected:
                raise forms.ValidationError(
                    Warnings.TASK_IN_A_BUDGET_BUT_BUDGET_IS_REJECTED)
            elif task.expense.approvement.is_rejected:
                raise forms.ValidationError(Warnings.TASK_EXPENSE_IS_REJECTED)

        '''validate if current state has approvement'''
        if task.state and not should_be_approved(task.state):
            raise forms.ValidationError(Warnings.CURRENT_TASK_IS_NOT_APPROVED)

        return self.cleaned_data

    class Meta:
        model = TaskState
        exclude = [
            'id', 'date_created', 'is_done', 'is_review_requested',
            'comments', 'request_review',
            'approvement', 'completion_date', 'author', 'approvements']


class ApproveTaskStateForm(
        forms.Form, InitialValidationMixin, FormControlMixin):
    __initial__ = ['fund', 'author', 'state', 'task']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

    is_rejected = forms.BooleanField(label='Reject', required=False)
    notes = forms.CharField(widget=forms.Textarea(),
                            label='Notes', required=False)

    def clean(self):
        author = self.initial['author']

        if should_be_approved(self.initial['state']):
            raise forms.ValidationError(Warnings.TASK_STATE_IS_APPROVED)

        if not author in [self.initial['state'].request_review.reviewer]:
            raise forms.ValidationError(
                Warnings.CURRENT_USER_IS_NOT_TASK_REVIEWER)

    def save(self):
        author = self.initial['author']
        state = self.initial['state']
        fund = self.initial['fund']

        approvement = Approvement.objects.create(
            author=author, fund=fund,
            notes=self.cleaned_data['notes'],
            is_rejected=self.cleaned_data['is_rejected'])

        state.approvement = approvement
        state.is_review_requested = False

        if approvement.is_rejected == False:
            state.completion_date = datetime.datetime.utcnow()
            state.is_done = True

        state.approvements.add(approvement)
        state.save()

        return state


class TaskCreateAttachmentForm(CreateAttachmentForm, InitialValidationMixin):
    __initial__ = ['fund', 'author', 'task']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)

    def save(self):
        task = self.initial['task']
        author = self.initial['author']
        fund = self.initial['fund']

        self.instance.author = author
        self.instance.fund = fund
        self.instance.save()

        task.attachments.add(self.instance)

        return self.instance


class TaskStateReviewRequestForm(
        forms.Form, InitialValidationMixin, FormControlMixin):
    __initial__ = ['fund', 'author', 'state', 'task']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

    notes = forms.CharField(widget=forms.Textarea(), min_length=10,
                            label='Message', required=True)

    def clean(self):
        if self.initial['author'] != self.initial['task'].assignee:
            raise forms.ValidationError(
                Warnings.CURRENT_USER_IS_NOT_TASK_ASSIGNEE)

        if self.initial['state'].is_review_requested:
            raise forms.ValidationError(
                Warnings.TASK_STATE_REVIEW_REQUEST_HAS_BEEN_SENT)

        if should_be_approved(self.initial['state']):
            raise forms.ValidationError(Warnings.TASK_STATE_IS_APPROVED)

        return self.cleaned_data

    def save(self):
        state = self.initial['state']
        state.is_review_requested = True
        state.save()

        review_request_created.send(
            sender=TaskState,
            instance=state,
            fund=self.initial['fund'],
            task=self.initial['task'],
            message=self.cleaned_data['notes']
        )

        return self.initial['state']
