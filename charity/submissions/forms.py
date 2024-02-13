from typing import Any
from django import forms

from commons.mixins import FormControlMixin, InitialValidationMixin

from mailings.models import MailingGroup, MailingTemplate
from wards.models import Ward

from .models import Submission, SubmissionSentStatus


class AddSubmissionForm(
        forms.ModelForm,
        FormControlMixin, InitialValidationMixin):
    __initial__ = ['fund', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)

        self.fields['author'].widget = forms.HiddenInput()
        self.fields['fund'].widget = forms.HiddenInput()
        self.fields['mailing_group'].queryset = MailingGroup.objects.filter(
            fund=self.fund)
        self.fields['mailing_template'].queryset = MailingTemplate.objects.filter(
            fund=self.fund)
        FormControlMixin.__init__(self)

    class Meta:
        model = Submission
        exclude = ['id', 'date_created', 'wards', 'is_draft', 'status']

    def save(self):
        if self.instance._state.adding:
            self.instance.is_draft = True
            self.instance.status = SubmissionSentStatus.DRAFT

        return super().save(True)
