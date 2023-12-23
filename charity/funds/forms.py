from django import forms

from .models import Fund


class FundForm(forms.ModelForm):
    class Meta:
        model = Fund
        exclude = ('date_created', )
