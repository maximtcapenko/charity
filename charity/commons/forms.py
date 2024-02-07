from django import forms
from django.db.models import Q

from .mixins import FormControlMixin, SearchFormMixin


class CustomLabeledModelChoiceField(forms.ModelChoiceField):
    def __init__(self, label_func, *args, **kwargs):
        self.lable_func = label_func
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        if self.lable_func:
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
