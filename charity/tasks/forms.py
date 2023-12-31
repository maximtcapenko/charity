from django import forms
from django.db.models import Max, Q, Exists, OuterRef
from django.contrib.auth.models import User

from commons.mixins import FormControlMixin
from processes.models import Process
from wards.models import Ward
from .models import Task


class CreateTaskForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['project'].widget = forms.HiddenInput()

        if (self.initial):
            project = self.initial['project']
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
