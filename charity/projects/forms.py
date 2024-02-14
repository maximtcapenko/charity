from django import forms
from django.db.models import Count, Q, Exists, OuterRef
from django.contrib.auth.models import User

from commons.mixins import InitialMixin, FormControlMixin, \
    SearchByNameMixin, SearchFormMixin
from commons.forms import user_model_choice_field, CustomLabeledModelChoiceField
from commons.functional import validate_modelform_field

from processes.models import Process

from .messages import Warnings
from .models import Project
from .querysets import get_avaliable_for_select_queryset


class CreateProjectForm(
        forms.ModelForm, InitialMixin, FormControlMixin):
    __initial__ = ['fund', 'author']

    field_order = ['name', 'leader']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.author.widget = forms.HiddenInput()
        self.form.fund.widget = forms.HiddenInput()
        self.form.leader = user_model_choice_field(
            fund=self.fund, label='Leader')

        FormControlMixin.__init__(self)

    class Meta:
        model = Project
        exclude = ['date_created', 'id', 'wards', 'closed_date',
                   'is_closed', 'cover', 'budget', 'processes', 'reviewers']


class UpdateProjectForm(CreateProjectForm):
    __initial__ = ['fund']

    def clean_leader(self):
        leader = self.cleaned_data.get('leader')
        if leader is None and self.instance.leader:
            raise forms.ValidationError(
                Warnings.PROJECT_LEADER_CANNOT_BE_UNDEFINED)
        return leader


class SearchProjetForm(forms.Form, FormControlMixin, SearchByNameMixin, SearchFormMixin):
    __resolvers__ = {
        'active_only': lambda field: Q(is_closed=False)
    }

    active_only = forms.BooleanField(label='Active', required=False)
    leader = forms.ModelChoiceField(
        queryset=User.objects, label='Leader', required=False)

    def __init__(self, fund, *args, **kwargs):
        super().__init__(*args, **kwargs)
        SearchByNameMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['active_only'].widget.attrs.update({
            'onchange': 'javascript:this.form.submit()'
        })

        self.fields['leader'].queryset = User.objects.filter(
            Q(volunteer_profile__fund=fund) & Exists(Project.objects.filter(fund=fund, leader=OuterRef('pk'))))
        self.fields['leader'].widget.attrs.update({
            'onchange': 'javascript:this.form.submit()'
        })
        self.__resolvers__['leader'] = lambda field: Q(leader=field)
        self.order_fields(['active_only', 'name'])


class AddProcessToProjectForm(
        forms.Form, InitialMixin, FormControlMixin):
    __initial__ = ['project']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.process = CustomLabeledModelChoiceField(
            label_func=lambda value: '%s (%s %s)' % (
                value.name, value.states_count, 'states' if value.states_count > 1 else 'state'),
            model=Process,
            queryset=get_avaliable_for_select_queryset(self.project), label='Process')

        FormControlMixin.__init__(self)

    process = forms.ModelChoiceField(
        Process.objects, required=True, label='Process')

    def clean_process(self):
        process = self.cleaned_data['process']
        if process.states.count() == 0:
            raise forms.ValidationError(
                Warnings.EMPTY_PROCESS_CANNOT_BE_ADDED)

        return process

    def save(self):
        process = self.cleaned_data['process']
        self.project.processes.add(process)
        self.project.save()

        return self.project


class AddProjectReviewerForm(
        forms.Form, InitialMixin, FormControlMixin):
    __initial__ = ['project']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.project.widget = forms.HiddenInput()
        self.form.reviewer = user_model_choice_field(queryset=User.objects.filter(
            Q(volunteer_profile__fund=self.project.fund) &
            ~Q(id__in=self.project.reviewers.values('id'))), label='Reviewer')

        FormControlMixin.__init__(self)

    project = forms.ModelChoiceField(Project.objects, required=True)

    def clean(self):
        validate_modelform_field('project', self.initial, self.cleaned_data)
        return self.cleaned_data

    def save(self):
        reviewer = self.cleaned_data['reviewer']
        self.project.reviewers.add(reviewer)

        return reviewer
