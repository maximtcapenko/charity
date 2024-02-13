from django import forms

from commons.functional import resolve_many_2_many_attr, resolve_rel_attr_path
from commons.mixins import FormControlMixin, FileUploadMixin, InitialMixin

from funds.models import Fund

from .models import Attachment


class CreateAttachmentForm(
        forms.ModelForm, InitialMixin, FormControlMixin,
        FileUploadMixin):
    __initial__ = ['target_id', 'target_content_type', 'author', 'fund']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.form.author.widget = forms.HiddenInput()

    def clean(self):
        content_type = self.target_content_type
        fund_attr_path = resolve_rel_attr_path(
            Fund, content_type.model_class())

        filter = {
            fund_attr_path: self.fund,
            'pk': self.target_id
        }

        if not content_type.model_class().objects.filter(**filter).exists():
            raise forms.ValidationError(
                'The author does not have permission to attach files to the item.')

        return self.cleaned_data

    def save(self):
        self.instance.fund = self.fund
        self.instance.author = self.author
        self.instance.save()
        
        files = resolve_many_2_many_attr(Attachment,
            self.target_content_type, self.target_id)
        files.add(self.instance)
        return self.instance

    class Meta:
        model = Attachment
        exclude = ['id', 'date_created', 'fund']
