from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import Budget, Income
from commons.mixins import FormControlMixin


class CreateBudgetForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

        if (self.initial):
            self.fields['manager'].queryset = User.objects \
                .filter(volunteer_profile__fund_id=self.initial['fund'].id) \
                .only('id', 'username')

    def save(self):
        author = self.initial['user']
        self.instance.author = author

        return super().save()

    class Meta:
        model = Budget
        exclude = ['id', 'date_creted',
                   'author', 'is_closed',
                   'approvement']


class CreateIncomeForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['budget'].widget = forms.HiddenInput()

    class Meta:
        model = Income
        exclude = ['id', 'author', 
                   'date_created', 'approvements',
                    'approvement']
