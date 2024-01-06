from django import forms
from django.db import models
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
        last_order_position = ProcessState.objects.filter(process__id=self.instance.process_id) \
            .aggregate(result=models.Max('order_position'))['result']
        self.instance.order_position = last_order_position + 1 if last_order_position else 1
        
        return super().save()


    class Meta:
        model = ProcessState
        exclude = ['id', 'date_created',
                   'is_inactive', 'order_position']
