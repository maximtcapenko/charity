from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

from .functional import get_reviewer_label
from .mixins import FormControlMixin, SearchFormMixin
from .utils import DictObjectWrapper


class CustomLabeledModelChoiceField(forms.ModelChoiceField):
    def __init__(self, label_func, *args, model=None, **kwargs):
        self.label_func = label_func
        self.model = model
        super().__init__(*args, **kwargs)

    def clean(self, value):
        if value and self.model:
            return self.model.objects.get(pk=value)

        return super().clean(value)

    def prepare_value(self, value):
        if isinstance(value, dict):
            value = DictObjectWrapper(value, model=self.model)

        return super().prepare_value(value)

    def label_from_instance(self, obj):
        if self.label_func:
            if isinstance(obj, dict):
                obj = DictObjectWrapper(obj)

            return self.label_func(obj)

        return super().label_from_instance(obj)


class ApprovedOnlySearchForm(forms.Form, FormControlMixin, SearchFormMixin):

    approved_only = forms.BooleanField(label='Approved', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.__resolvers__ = {
        'approved_only': lambda field: Q(approvement__is_rejected=False)
    }
        FormControlMixin.__init__(self)

        self.fields['approved_only'].widget.attrs.update({
            'onchange': 'javascript:this.form.submit()'
        })


def user_model_choice_field(fund=None, required=None, queryset=None, **kwargs):
    return CustomLabeledModelChoiceField(
        label_func=get_reviewer_label,
        queryset=User.objects.select_related(
            'volunteer_profile').filter(volunteer_profile__fund=fund) if queryset is None else queryset,
        required=True if required is None else required, **kwargs)


class DateRangeField(forms.CharField):
    def __init__(self, date_format, *args, **kwagrs):
        self.date_format = date_format
        super().__init__(*args, **kwagrs)

    def clean(self, value):
        from datetime import datetime

        value = super().clean(value)
        if not value:
            return None
        try:
            start_str, end_str = value.split(' - ')
            start_date = datetime.strptime(start_str.strip(), self.date_format).date()
            end_date = datetime.strptime(end_str.strip(), self.date_format).date()
            
            return start_date, end_date
        except (ValueError, IndexError):
            raise forms.ValidationError(
                f'Invalid date range format. Please use {self.date_format} - {self.date_format}.'
            )
