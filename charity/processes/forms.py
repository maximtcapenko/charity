from django import forms
from django.db.models import Max, F
from .models import Process, ProcessState
from commons.mixins import FormControlMixin, InitialMixin


class CreateProcessForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    class Meta:
        model = Process
        exclude = ['id', 'date_created']


class CreateProcessStateForm(
        forms.ModelForm, InitialMixin,
        FormControlMixin):
    __initial__ = ['process']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.process.widget = forms.HiddenInput()

        if self.instance._state.adding:
            self.fields['after_state'] = forms.ModelChoiceField(
                self.process.states.order_by(
                    'order_position'), required=False, label='Insert after state', empty_label='Select state')

        FormControlMixin.__init__(self)

    def save(self):
        if self.instance._state.adding:
            after_state = self.cleaned_data.get('after_state')
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
