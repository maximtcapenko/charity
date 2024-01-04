import datetime

from django import forms
from django.db.models import Max, Q, Exists, OuterRef
from django.contrib.auth.models import User

from commons.mixins import FormControlMixin
from commons.functions import get_argument_or_error
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
        exclude = ['date_created', 'id', 'expense', 'state',
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
        if task.state:
            next_state = task.state.state.next_state
            queryset = ProcessState.objects.filter(id=next_state.id)
        else:
            queryset = ProcessState.objects.filter(
                Q(process__id=task.process_id) & ~Q(id=task.state_id)
            )
        self.fields['state'].queryset = queryset

    class Meta:
        model = TaskState
        exclude = ['id', 'date_created']
