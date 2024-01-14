from django import forms
from django.db.models import Count, Q, Exists, OuterRef
from django.contrib.auth.models import User

from commons.mixins import InitialValidationMixin, FormControlMixin, require_initial
from commons.functions import validate_modelform_field

from .models import Project
from processes.models import Process, ProcessState
from wards.models import Ward


class CreateProjectForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['fund']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        fund = self.initial['fund']

        self.fields['fund'].widget = forms.HiddenInput()
        self.fields['leader'].queryset = User.objects \
            .filter(volunteer_profile__fund_id=fund.id) \
            .only('id', 'username')

    class Meta:
        model = Project
        exclude = ['date_created', 'id', 'wards', 'closed_date',
                   'is_closed', 'cover', 'budget', 'processes', 'reviewers']


class UpdateProjectForm(CreateProjectForm):
    def clean_leader(self):
        leader = self.cleaned_data.get('leader')
        if leader is None and self.instance.leader:
            raise forms.ValidationError(
                'Leader is already assigned and can not be empty')
        return leader


class AddWardToProjectForm(
        forms.Form, InitialValidationMixin, FormControlMixin):
    __initial__ = ['project']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['ward'].queryset = Ward.active_objects.filter(
            Q(fund__id=self.initial['project'].fund_id) &
            Q(projects__isnull=True) | Q(projects__is_closed=True)
        ).only('id', 'name')

    ward = forms.ModelChoiceField(Ward.objects, required=True, label='Ward')

    def save(self):
        project = self.initial['project']
        ward = self.cleaned_data['ward']
        project.wards.add(ward)
        project.save()

        return project


class AddProcessToProjectForm(
        forms.Form, InitialValidationMixin, FormControlMixin):
    class ProcessModelChoiceField(forms.ModelChoiceField):
        def clean(self, value):
            if value:
                return Process.objects.get(pk=value)
            return super().clean(value)

        def prepare_value(self, value):
            if value and isinstance(value, dict):
                return value['id']
            return super().prepare_value(value)

        def label_from_instance(self, obj):
            states_count = obj['states_count']
            name =  obj['name']
            return '%s (%s %s)' % (name, states_count, 'states' if states_count > 1 else 'state')

    __initial__ = ['project']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)

        project = self.initial['project']
        self.fields['process'] = AddProcessToProjectForm.ProcessModelChoiceField(
            queryset=Process.objects.filter(
            Exists(ProcessState.objects.filter(process=OuterRef('pk'))) &
            Q(is_inactive=False, fund__id=project.fund_id) &
            ~Q(projects__in=[project]))
            .annotate(states_count=Count('states', distinct=True))
            .values('id', 'name', 'states_count'), label='Process')
        
        FormControlMixin.__init__(self)

    process = forms.ModelChoiceField(
        Process.objects, required=True, label='Process')

    def clean_process(self):
        process = self.cleaned_data['process']
        if process.states.count() == 0:
            raise forms.ValidationError('Process with 0 states can not be added to project')
        
        return process

    def save(self):
        project = self.initial['project']
        process = self.cleaned_data['process']
        project.processes.add(process)
        project.save()

        return project


class AddProjectReviewerForm(
        forms.Form, InitialValidationMixin, FormControlMixin):
    __initial__ = ['project']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        project = self.initial['project']

        self.fields['project'].widget = forms.HiddenInput()
        self.fields['reviewer'].queryset = User.objects.filter(
            Q(volunteer_profile__fund__id=project.fund_id) &
            ~Q(id__in=project.reviewers.values('id')))

    reviewer = forms.ModelChoiceField(
        User.objects, label='Reviewer', required=True)
    project = forms.ModelChoiceField(Project.objects, required=True)

    def clean(self):
        validate_modelform_field('project', self.initial, self.cleaned_data)
        return self.cleaned_data

    def save(self):
        project = self.initial['project']
        reviewer = self.cleaned_data['reviewer']
        project.reviewers.add(reviewer)

        return reviewer
