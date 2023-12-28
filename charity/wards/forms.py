from django import forms
from .models import Ward
from commons.mixins import FormControlMixin


class CreateWardForm(forms.ModelForm, FormControlMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    class Meta:
        model = Ward
        exclude = ['id','attachments','cover']
