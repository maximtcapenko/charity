from django import forms
from django.contrib.auth.models import User

from commons.mixins import FormControlMixin, InitialValidationMixin, FileUploadMixin
from commons.functional import validate_modelform_field
from .models import Fund, Contribution, Contributor, VolunteerProfile


class FundForm(forms.ModelForm):
    class Meta:
        model = Fund
        exclude = ('date_created', )


class CreateContributionForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['fund', 'author']

    field_order = ['contributor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()
        self.fields['contributor'].queryset = Contributor.objects \
            .filter(fund=self.fund, is_internal=False)

    def clean(self):
        validate_modelform_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    def save(self):
        self.instance.author = self.author

        return super().save()

    class Meta:
        model = Contribution
        exclude = ['id', 'date_created', 'author']


class CreateVolunteerForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['fund']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['user'].queryset = User.objects.filter(
            volunteer_profile__isnull=True,
            is_active=True
        )
        self.fields['fund'].widget = forms.HiddenInput()

    def clean(self):
        validate_modelform_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    class Meta:
        model = VolunteerProfile
        exclude = ['id', 'date_created', 'cover']


class CreateContributorForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin, FileUploadMixin):
    __initial__ = ['fund']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    def clean(self):
        validate_modelform_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    class Meta:
        model = Contributor
        exclude = ['id', 'date_created']


class UpdateVolunteerProfile(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['fund']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    def clean(self):
        validate_modelform_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    class Meta:
        model = VolunteerProfile
        exclude = ['id',
                   'date_created',
                   'user',
                   'cover']
