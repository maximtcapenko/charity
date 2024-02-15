from django import forms
from django.db.models import Exists, OuterRef

from commons.mixins import FormControlMixin, FormFieldsWrapperMixin, InitialMixin, \
    SearchByNameMixin, SearchFormMixin
from commons.functional import resolve_many_2_many_attr_path
from filters.models import Filter

from customfields.forms import BaseCustomFieldsModelForm
from projects.models import Project
from tasks.models import Task

from .models import Ward


class CreateWardForm(BaseCustomFieldsModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    class Meta:
        model = Ward
        exclude = ['id', 'attachments', 'cover', 'comments']


class SearchWardForm(forms.Form, FormControlMixin, SearchByNameMixin, SearchFormMixin, FormFieldsWrapperMixin):
    __resolvers__ = {}

    def __init__(self, fund, *args, **kwargs):
        super().__init__(*args, **kwargs)
        SearchByNameMixin.__init__(self)
        FormFieldsWrapperMixin.__init__(self)

        self.form.in_work_only = forms.BooleanField(
            label='In work', required=False,
            widget=forms.CheckboxInput(attrs={
                'div_class': 'col-2',
                'onchange': 'javascript:this.form.submit()'}))
        self.form.not_in_work = forms.BooleanField(
            label='Available', required=False,
            widget=forms.CheckboxInput(attrs={
                'div_class': 'col-2',
                'onchange': 'javascript:this.form.submit()'}))

        filter = forms.ModelChoiceField(queryset=Filter.objects.filter(
            fund=fund, content_type__model='ward'), required=False, label='Filter')
        filter.widget.attrs.update({
            'onchange': 'javascript:this.form.submit()'
        })

        self.fields['filter'] = filter

        self.__resolvers__['filter'] = self.apply_customfields_filter
        self.__resolvers__['in_work_only'] = lambda field: Exists(
            Task.objects.filter(is_done=False, ward=OuterRef('pk')))
        self.__resolvers__['not_in_work'] = lambda field: ~Exists(
            Project.objects.filter(is_closed=False, wards__in=OuterRef('pk')))

        self.order_fields(['in_work_only', 'not_in_work'])
        FormControlMixin.__init__(self)

    def apply_customfields_filter(self, filter):
        search_fields = filter.expressions.filter(
            field__is_searchable=True).all()
        return [field.get_expression(Ward) for field in search_fields]


class AttachWardToTargetForm(
        forms.Form, InitialMixin):
    __initial__ = ['target']

    def __init__(self, *args, validators=None, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)
        self.validators = validators

    ward = forms.ModelChoiceField(Ward.objects, required=True, label='Ward')

    def clean(self):
        if self.validators:
            for validator in self.validators:
                validator(self.cleaned_data['ward'])

        return self.cleaned_data

    def save(self):
        target = self.target
        ward = self.cleaned_data['ward']

        target_attr = resolve_many_2_many_attr_path(Ward, target.__class__)
        target_wards = getattr(target, target_attr)
        target_wards.add(ward)

        return target
