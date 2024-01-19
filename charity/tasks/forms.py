import datetime

from django import forms
from django.db.models import Max
from django.contrib.auth.models import User

from commons.functions import should_be_approved
from commons.mixins import FormControlMixin, InitialValidationMixin
from files.forms import CreateAttachmentForm
from funds.models import Approvement
from processes.models import Process

from .querysets import get_available_task_process_states_queryset, \
    get_available_task_rewiewers_queryset, get_available_project_wards_queryset
from .models import Task, TaskState
from .signals import review_request_created


class CreateTaskForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['project', 'author']
    field_order = ['ward']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['project'].widget = forms.HiddenInput()

        project = self.initial['project']
        self.fields['assignee'].queryset = User.objects \
            .filter(volunteer_profile__fund_id=project.fund_id) \
            .only('id', 'username')

        self.fields['reviewer'].queryset = project.reviewers
        self.fields['ward'].queryset = get_available_project_wards_queryset(
            project).only('id', 'name')

        self.fields['process'].queryset = Process.objects \
            .filter(projects__in=[project]) \
            .only('id', 'name')

    def clean(self):
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']

        reviewer = self.cleaned_data['reviewer']
        assignee = self.cleaned_data['assignee']
        if reviewer == assignee:
            raise forms.ValidationError('Assignee can not be reviewer')

        if not self.initial['project'].reviewers.contains(reviewer):
            raise forms.ValidationError(
                'Reviewer is not in list of project reviewers')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                'End date can not be less then start date')

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
                   'states', 'subscribers', 'author',
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
            raise forms.ValidationError('Reviewer can not be assignee of task')

        '''validate if budget of task is approved'''
        if task.should_be_approved:
            if task.expense == None:
                raise forms.ValidationError(
                    'Current task has estimation but not included to any budget')
            elif task.expense.budget.approvement == None:
                raise forms.ValidationError(
                    'Current task has estimation but budget is not approved yet')
            elif task.expense.budget.approvement.is_rejected:
                raise forms.ValidationError(
                    'Current task has estimation but budget has been rejected')
            elif task.expense.approvement.is_rejected:
                raise forms.ValidationError(
                    'Current task has estimation but it has been rejected')

        '''validate if current state has approvement'''
        if task.state and not should_be_approved(task.state):
            raise forms.ValidationError('Current task state is not approved')

        return self.cleaned_data

    class Meta:
        model = TaskState
        exclude = [
            'id', 'date_created', 'is_done', 'is_review_requested', 'comments',
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
        task = self.initial['task']

        if task.reviewer != author or self.initial['state'].reviewer != author:
            raise forms.ValidationError('Current user is not task reviewer')

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
            raise forms.ValidationError('Current user is not assignee of task')

        if self.initial['state'].is_review_requested:
            raise forms.ValidationError('Review requeset already sent')

        if should_be_approved(self.initial['state']):
            raise forms.ValidationError('Current state is approved')

        return self.cleaned_data

    def save(self):
        state = self.initial['state']
        state.is_review_requested = True
        state.save()

        review_request_created.send(
            sender=TaskState,
            instance=state,
            task=self.initial['task'],
            message=self.cleaned_data['notes']
        )

        return self.initial['state']
