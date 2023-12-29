from typing import Any
from django import forms
from .models import Process, ProcessState
from commons.mixins import FormControlMixin


class CreateProcessForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    class Meta:
        model = Process
        exclude = ['id', 'date_created']


class CreateProcessStateForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['process'].widget = forms.HiddenInput()

    def save(self):
        prev_state = ProcessState.objects.filter(
            next_state__isnull=True).first()
        self.instance.is_first = True if prev_state is None else False

        instance = super().save()

        if prev_state:
            prev_state.next_state = instance
            prev_state.save()

        return instance

    class Meta:
        model = ProcessState
        exclude = ['id', 'date_created',
                   'is_inactive', 'is_first', 'next_state']
