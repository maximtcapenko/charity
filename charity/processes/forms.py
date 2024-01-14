from django import forms
from django.db.models import Max, F
from .models import Process, ProcessState
from commons.mixins import FormControlMixin, InitialValidationMixin


class CreateProcessForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    class Meta:
        model = Process
        exclude = ['id', 'date_created']


class UpdateProcessForm(CreateProcessForm):
    pass


class CreateProcessStateForm(
        forms.ModelForm, InitialValidationMixin,
        FormControlMixin):
    __initial__ = ['process']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['process'].widget = forms.HiddenInput()
        self.fields['after_state'].queryset = self.initial['process'].states.order_by('order_position')
        self.fields['after_state'].empty_label = 'Select state'

    after_state = forms.ModelChoiceField(
        ProcessState.objects, required=False, label='Insert after state')

    def save(self):
        after_state = self.cleaned_data['after_state']
        if after_state:
            ProcessState.objects.filter(
                process__id=self.instance.process_id,
                order_position__gt=after_state.order_position).update(order_position=F('order_position') + 1)
            
            self.instance.order_position = after_state.order_position + 1
            self.instance.save()

        else:
            last_order_position = ProcessState.objects.filter(process__id=self.instance.process_id) \
                .aggregate(result=Max('order_position'))['result']
            self.instance.order_position = last_order_position + 1 if last_order_position else 1
            self.instance.save()

        return self.instance

    class Meta:
        model = ProcessState
        exclude = ['id', 'date_created',
                   'is_inactive', 'order_position']
