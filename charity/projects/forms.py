from django import forms
from django.db.models import Q, Exists, OuterRef
from django.contrib.auth.models import User

from commons.mixins import FormControlMixin
from commons.functions import get_argument_or_error

from .models import Project
from processes.models import Process, ProcessState
from wards.models import Ward


class CreateProjectForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()
        if (self.initial):
            fund = get_argument_or_error('fund', self.initial)
            self.fields['leader'].queryset = User.objects \
                .filter(volunteer_profile__fund_id=fund.id) \
                .only('id', 'username')

    class Meta:
        model = Project
        exclude = ['date_created', 'id', 'wards', 'closed_date',
                   'is_closed', 'cover', 'budget', 'processes']


class UpdateProjectForm(CreateProjectForm):
    def clean_leader(self):
        leader = self.cleaned_data.get('leader')
        if leader is None and self.instance.leader:
            raise forms.ValidationError(
                'Leader is already assigned and can not be empty')
        return leader


class AddWardToProjectForm(forms.Form, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        if self.initial:
            project = get_argument_or_error('project', self.initial)
            self.fields['ward'].queryset = Ward.active_objects.filter(
                Q(fund__id=project.fund_id) &
                Q(projects__isnull=True) | Q(projects__is_closed=True)
            ).only('id', 'name')

    ward = forms.ModelChoiceField(Ward.objects, required=True, label='Ward')

    def save(self):
        project = get_argument_or_error('project', self.initial)
        ward = self.cleaned_data['ward']
        project.wards.add(ward)
        project.save()

        return project


class AddProcessToProjectForm(forms.Form, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        if self.initial:
            project = get_argument_or_error('project', self.initial)
            self.fields['process'].queryset = Process.objects.filter(
                Q(Exists(ProcessState.objects.filter(process=OuterRef('pk')))) &
                Q(is_inactive=False, fund__id=project.fund_id) &
                ~Q(projects__in=[project])
            ).only('id', 'name')

    process = forms.ModelChoiceField(
        Process.objects, required=True, label='Process')
    
    def save(self):
        project = get_argument_or_error('project', self.initial)
        process = self.cleaned_data['process']
        project.processes.add(process)
        project.save()

        return project
