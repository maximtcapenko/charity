from django import forms
from django.contrib.auth.models import User

from commons.mixins import FormControlMixin
from commons.functions import get_argument_or_error, validate_form_field
from .models import Fund, Contribution, Contributor, VolunteerProfile


class FundForm(forms.ModelForm):
    class Meta:
        model = Fund
        exclude = ('date_created', )


class CreateContributionForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        fund = get_argument_or_error('fund', self.initial)

        self.fields['fund'].widget = forms.HiddenInput()
        self.fields['contributor'].queryset = Contributor.objects \
            .filter(fund__id=fund.id)

    def clean(self):
        validate_form_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    def save(self):
        user = get_argument_or_error('user', self.initial)
        self.instance.author = user
        return super().save()

    class Meta:
        model = Contribution
        exclude = ['id', 'date_created', 'author']


class CreateVolunteerForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['user'].queryset = User.objects.filter(
            volunteer_profile__isnull=True,
            is_active=True
        )
        self.fields['fund'].widget = forms.HiddenInput()

    def clean(self):
        validate_form_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    class Meta:
        model = VolunteerProfile
        exclude = ['id', 'date_created', 'cover']


class CreateContributorForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    def clean(self):
        validate_form_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    class Meta:
        model = Contributor
        exclude = ['id', 'date_created']


class UpdateVolunteerProfile(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    def clean(self):
        validate_form_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    class Meta:
        model = VolunteerProfile
        exclude = ['id',
                   'date_created',
                   'user',
                   'cover']
