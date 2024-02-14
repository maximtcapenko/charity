from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

from .functional import get_reviewer_label
from .mixins import FormControlMixin, SearchFormMixin
from .utils import DictObjectWrapper


class CustomLabeledModelChoiceField(forms.ModelChoiceField):
    def __init__(self, label_func, *args, model=None, **kwargs):
        self.lable_func = label_func
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
        if self.lable_func:
            if isinstance(obj, dict):
                obj = DictObjectWrapper(obj)

            return self.lable_func(obj)

        return super().label_from_instance(obj)


class ApprovedOnlySearchForm(forms.Form, FormControlMixin, SearchFormMixin):
    __resolvers__ = {
        'approved_only': lambda field: Q(approvement__is_rejected=False)
    }

    approved_only = forms.BooleanField(label='Approved', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
