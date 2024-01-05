from django import forms
from django.db.models import Max, Q, Exists, OuterRef
from django.contrib.auth.models import User

from commons.mixins import FormControlMixin
from commons.functions import get_argument_or_error
from funds.models import Approvement
from processes.models import Process, ProcessState
from wards.models import Ward
from .models import Comment, Task, TaskState


class CreateTaskForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['project'].widget = forms.HiddenInput()

        if (self.initial):
            project = get_argument_or_error('project', self.initial)
            self.fields['assignee'].queryset = User.objects \
                .filter(volunteer_profile__fund_id=project.fund_id) \
                .only('id', 'username')

            self.fields['ward'].queryset = Ward.active_objects. \
                filter(Q(projects__in=[project])
                       & ~Exists(Task.objects.filter(ward=OuterRef("pk"),
                                                     project__id=project.id))) \
                .only('id', 'name')

            self.fields['process'].queryset = Process.objects \
                .filter(projects__in=[project]) \
                .only('id', 'name')

    def save(self):
        last_order_position = Task.objects.filter(project__id=self.instance.project_id) \
            .aggregate(result=Max('order_position'))['result']
        self.instance.order_position = last_order_position + 1 if last_order_position else 1

        return super().save()

    class Meta:
        model = Task
        exclude = ['date_created', 'id', 'expense', 'state', 'states',
                   'attachments', 'order_position', 'is_done', 'is_started']


class UpdateTaskForm(CreateTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields['ward'].queryset = Ward.active_objects. \
                filter(Q(projects__in=[self.instance.project])
                       & ~Exists(Task.objects.filter(Q(ward=OuterRef("pk"),
                                                     project__id=self.instance.project.id)
                                                     & ~Q(id=self.instance.id)))) \
                .only('id', 'name')

            if self.instance.expense and \
               self.instance.expense.approvement.is_rejected == False:
                self.fields.pop('estimated_expense_amount')

            if self.instance.state_id:
                self.fields.pop('process')

    def save(self):
        self.instance.save()
        return self.instance


class CreateCommentForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        # self.fields['tagged_interlocutors'].queryset = User.objects \
        #        .filter(Q(volunteer_profile__fund_id=user.volunteer_profile.fund_id) &
        #                ~Q(id=user.id)) \
        #        .only('id', 'username')
        self.fields['author'].widget = forms.HiddenInput()

    def save(self):
        self.instance.task = self.initial['task']

        return super().save()

    class Meta:
        model = Comment
        exclude = ['id', 'task', 'reply', 'tagged_interlocutors']


class ActivateTaskStateForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        task = get_argument_or_error('task', self.initial)

        current_state = task.state
        if current_state:
            queryset = Q(process__id=task.process_id) & ~Q(
                id=current_state.state_id)
        else:
            queryset = Q(process__id=task.process_id)

        self.fields['state'].queryset = ProcessState.objects.filter(
            queryset).order_by('order_position')

    def save(self):
        author = get_argument_or_error('user', self.initial)
        task = get_argument_or_error('task', self.initial)
        self.instance.author = author
        self.instance.save()

        task.state = self.instance
        task.states.add(self.instance)
        task.save()

        return self.instance

    def clean(self):
        task = get_argument_or_error('task', self.initial)
        if task.state and not task.state.approvement_id:
            raise forms.ValidationError('Current task state is not approved')

        return self.cleaned_data

    class Meta:
        model = TaskState
        exclude = [
            'id', 'date_created',
            'approvement', 'prev_state',
            'completion_date', 'author', 'approvements']


class ApproveTaskStateForm(forms.Form, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

    is_rejected = forms.BooleanField(label='Reject', required=False)
    notes = forms.CharField(widget=forms.Textarea(),
                            label='Notes', required=False)

    def save(self):
        user = get_argument_or_error('user', self.initial)
        state = get_argument_or_error('state', self.initial)
        fund = get_argument_or_error('fund', self.initial)

        approvement = Approvement.objects.create(
            author=user, fund=fund,
            notes=self.cleaned_data['notes'],
            is_rejected=self.cleaned_data['is_rejected'])

        state.approvement = approvement
        state.approvements.add(approvement)
        state.save()

        return state
