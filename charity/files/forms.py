from django import forms

from commons.mixins import FormControlMixin, FileUploadMixin
from .models import Attachment


class CreateAttachmentForm(forms.ModelForm, FormControlMixin,
                           FileUploadMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

    class Meta:
        model = Attachment
        exclude = ['id', 'date_created', 'author', 'fund']
