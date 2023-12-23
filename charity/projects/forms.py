from django import forms
from django.contrib.auth.models import User

from commons.mixins import FormControlMixin
from .models import Project

class ProjectForm(forms.ModelForm, FormControlMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()
        self.fields['leader'].queryset = User.objects \
            .filter(volunteer_profile__fund_id=self.initial['fund'].id)

    cover = forms.FileField(allow_empty_file=True, required=False)

    class Meta:
        model = Project
        exclude = ['date_created', 'id', 'wards', 'is_closed']
