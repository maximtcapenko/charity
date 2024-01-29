from django import forms

from commons.mixins import FormControlMixin

from customfields.forms import BaseCustomFieldsModelForm
from .models import Ward


class CreateWardForm(BaseCustomFieldsModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    class Meta:
        model = Ward
        exclude = ['id', 'attachments', 'cover']
