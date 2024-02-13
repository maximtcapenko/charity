from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, Q, OuterRef

from ckeditor.widgets import CKEditorWidget
from django.urls import reverse

from commons.mixins import FormControlMixin, InitialMixin
from commons.forms import CustomLabeledModelChoiceField
from funds.models import Contributor

from .models import MailingGroup, MailingTemplate
from .widgets import TemplateFieldsField


class AddMailingGroupForm(forms.ModelForm, FormControlMixin, InitialMixin):
    __initial__ = ['fund', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.fund.widget = forms.HiddenInput()
        self.form.author.widget = forms.HiddenInput()

        FormControlMixin.__init__(self)

    def clean(self):
        if self.initial['fund'] != self.cleaned_data['fund']:
            raise forms.ValidationError(
                'Creating group does not belong to current fund.')

        if self.initial['author'] != self.cleaned_data['author']:
            raise forms.ValidationError(
                'Author does not belong to current fund.')

        return self.cleaned_data

    class Meta:
        model = MailingGroup
        exclude = ['id', 'date_created', 'recipients']


class AddMailingRecipientForm(forms.Form, FormControlMixin, InitialMixin):
    __initial__ = ['fund', 'group']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.recipient = CustomLabeledModelChoiceField(
            label='Recipient', required=True,
            label_func=lambda x: f'{x.name} ({x.email})',
            queryset=Contributor.objects.filter(
                Q(fund=self.fund, is_internal=False)
                & ~Exists(self.group.recipients.filter(id=OuterRef('pk')))))

        FormControlMixin.__init__(self)

    def save(self):
        group = self.initial['group']
        group.recipients.add(self.cleaned_data['recipient'])


class AddMailingTemplateForm(forms.ModelForm, FormControlMixin, InitialMixin):
    __initial__ = ['fund', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)
        
        self.form.fund.widget = forms.HiddenInput()
        self.form.author.widget = forms.HiddenInput()
        self.form.content_type.queryset = ContentType.objects.filter(
            model__in=[
                'ward'])

        info = TemplateFieldsField(
            required=False,
            relation_id='id_content_type',
            fetch_url=reverse('mailings:get_content_type_details'))

        if hasattr(self.instance, 'content_type'):
            info.content_type = self.instance.content_type

        self.form.info = info
        self.form.template.widget = CKEditorWidget(
            config_name='basic_ckeditor')

        for field in self.fields:
            if hasattr(self.fields[field], 'widget'):
                self.fields[field].widget.attrs.update({
                    'placeholder': self.fields[field].label
                })
        FormControlMixin.__init__(self)

    class Meta:
        model = MailingTemplate
        exclude = ['id', 'date_created']
