from django import forms

from commons.mixins import FormControlMixin, InitialMixin
from mailings.models import MailingGroup, MailingTemplate

from .models import Submission, SubmissionSentStatus


class AddSubmissionForm(
        forms.ModelForm,
        FormControlMixin, InitialMixin):
    __initial__ = ['fund', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.author.widget = forms.HiddenInput()
        self.form.fund.widget = forms.HiddenInput()
        self.form.mailing_group.queryset = MailingGroup.objects.filter(
            fund=self.fund)
        self.form.mailing_template.queryset = MailingTemplate.objects.filter(
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
