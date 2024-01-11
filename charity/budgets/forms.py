from django import forms
from django.contrib.auth.models import User
from django.db import models

from commons.mixins import FormControlMixin
from commons.functions import get_argument_or_error, validate_modelform_field

from funds.models import Approvement
from .models import Budget, Income, Contribution


class CreateBudgetForm(forms.ModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

        fund = get_argument_or_error('fund', self.initial)

        self.fields['manager'].queryset = User.objects \
            .filter(volunteer_profile__fund_id=fund.id) \
            .only('id', 'username')

    def clean(self):
        validate_modelform_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    def save(self):
        user = get_argument_or_error('user', self.initial)
        self.instance.author = user

        return super().save()

    class Meta:
        model = Budget
        exclude = ['id', 'date_creted',
                   'author', 'is_closed',
                   'approvement', 'approvements', 'reviewers']


class UpdateBudgetForm(CreateBudgetForm):
    def clean(self):
        if self.instance.is_closed:
            raise forms.ValidationError(
                'Budget is closed and can not be edited')

        if self.instance.approvement:
            raise forms.ValidationError(
                'Budget is approved and can not be edited')

        validate_modelform_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    def clean_manager(self):
        manager = self.cleaned_data['manager']
        if manager is None and self.instance.manager:
            raise forms.ValidationError(
                'Manager is already assigned and can not be empty')
        return manager


class CreateIncomeForm(forms.ModelForm, FormControlMixin):
    class ContributionModelChoiceField(forms.ModelChoiceField):
        def clean(self, value):
            if value:
                return Contribution.objects.get(pk=value)
            return super().clean(value)

        def prepare_value(self, value):
            if value and isinstance(value, dict):
                return value['id']
            return super().prepare_value(value)

        def label_from_instance(self, obj):
            return '%s (%s)' % (
                obj['contribution_date'].strftime('%Y-%m-%d %H:%M'),
                obj['amount'] - obj['reserved_amount'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        budget = get_argument_or_error('budget', self.initial)

        self.fields['contribution'] = CreateIncomeForm.ContributionModelChoiceField(
            queryset=Contribution.objects.filter(
                fund__id=budget.fund_id).annotate(
                reserved_amount=models.Sum('incomes__amount', default=0))
            .values(
                'id', 'contribution_date',
                    'amount', 'reserved_amount'), label='Contribution')

        FormControlMixin.__init__(self)

        self.fields['budget'].widget = forms.HiddenInput()

    def save(self):
        user = get_argument_or_error('user', self.initial)
        self.instance.author = user
        return super().save()

    def clean(self):
        budget = get_argument_or_error('budget', self.initial)
        if budget.approvement_id:
            forms.ValidationError(
                'Can not add new income record, current budget is approved')

        contribution = self.cleaned_data['contribution']
        amount = self.cleaned_data['amount']
        reserved_amount = contribution.incomes.aggregate(
            total=models.Sum('amount', default=0))['total']

        if (contribution.amount - reserved_amount) < amount:
            raise forms.ValidationError('No avaliable contribution amount')
        elif amount <= 0:
            raise forms.ValidationError('Income can not be empty or negative')

        return self.cleaned_data

    class Meta:
        model = Income
        exclude = ['id', 'author',
                   'date_created', 'approvements',
                   'approvement']


class BaseApproveForm(forms.Form, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

    is_rejected = forms.BooleanField(label='Reject', required=False)
    notes = forms.CharField(widget=forms.Textarea(),
                            label='Notes', required=False)

    def save(self):
        user = get_argument_or_error('user', self.initial)
        fund = get_argument_or_error('fund', self.initial)
        target = get_argument_or_error('target', self.initial)

        approvement = Approvement.objects.create(
            author=user, fund=fund,
            notes=self.cleaned_data['notes'],
            is_rejected=self.cleaned_data['is_rejected'])

        target.approvement = approvement
        target.approvements.add(approvement)
        target.save()

        return target


class BudgetItemApproveForm(BaseApproveForm):
    def clean(self):
        target = get_argument_or_error('target', self.initial)
        user = get_argument_or_error('user', self.initial)

        """Validate user access"""
        if not target.budget.reviewers.filter(id=user.id).exists():
            raise forms.ValidationError(
                'Current user is not budget reviewer, only reviewers can approve budget items')
        
        if target.budget.approvement and target.budget.approvement.is_rejected == False:
            raise forms.ValidationError(
                'Item can not be approved because budget is approved')


class ApproveBudgetForm(BaseApproveForm):
    def clean(self):
        budget = get_argument_or_error('target', self.initial)
        user = get_argument_or_error('user', self.initial)

        """Validate user access"""
        if not budget.reviewers.filter(id=user.id).exists():
            raise forms.ValidationError(
                'Current user is not budget reviewer, only reviewers can approve budget')

        incomes = budget.incomes.exists()
        expenses = budget.expenses.exists()

        if incomes == False or expenses == False:
            raise forms.ValidationError(
                'Budget can not be approved, no incomes or expenses')

        unapproved_incomes = budget.incomes.filter(
            approvement_id__isnull=True).exists()

        unapproved_expenses = budget.expenses.filter(
            approvement_id__isnull=True).exists()

        if unapproved_incomes or unapproved_expenses:
            raise forms.ValidationError(
                'Budget can not be approved, there are not approved items')

        return self.cleaned_data


class AddBudgetReviewerForm(forms.Form, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['budget'].widget = forms.HiddenInput()
        budget = get_argument_or_error('budget', self.initial)
        self.fields['reviewer'].queryset = User.objects.filter(
            models.Q(volunteer_profile__fund__id=budget.fund_id) &
            ~models.Q(id__in=budget.reviewers.values('id')))

    reviewer = forms.ModelChoiceField(
        User.objects, label='Reviewer', required=True)
    budget = forms.ModelChoiceField(Budget.objects, required=True)

    def clean(self):
        validate_modelform_field('budget', self.initial, self.cleaned_data)
        budget = self.cleaned_data['budget']

        if budget.approvement \
                and budget.approvement.is_rejected == False:
            raise forms.ValidationError(
                'Reviewer can not be added because budget is approved')

        return self.cleaned_data

    def save(self):
        budget = get_argument_or_error('budget', self.initial)
        reviewer = self.cleaned_data['reviewer']
        budget.reviewers.add(reviewer)

        return reviewer
