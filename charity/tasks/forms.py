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

    def save(self, commit):
        last_order_position = Task.objects.filter(project__id=self.instance.project_id) \
            .aggregate(result=Max('order_position'))['result']
        self.instance.order_position = last_order_position + 1 if last_order_position else 1

        return super().save(commit)

    class Meta:
        model = Task
        exclude = ['date_created', 'id', 'expense', 'state',
                   'attachments', 'order_position', 'is_done', 'is_started']
