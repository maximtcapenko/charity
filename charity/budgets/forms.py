from typing import Any
from django import forms
from django.contrib.auth.models import User
from django.db import models

from commons.mixins import InitialValidationMixin, FormControlMixin
from commons.functions import validate_modelform_field, should_be_approved

from funds.models import Approvement
from tasks.models import Expense, Task

from .functions import get_budget_available_income
from .models import Budget, Income, Contribution
from .signals import exprense_created, budget_intem_reviewer_assigned


class CreateBudgetForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['fund', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self, *args, **kwargs)
        FormControlMixin.__init__(self, *args, **kwargs)

        fund = self.initial['fund']

        self.fields['fund'].widget = forms.HiddenInput()
        self.fields['manager'].queryset = User.objects \
            .filter(volunteer_profile__fund_id=fund.id) \
            .only('id', 'username')

    def clean(self):
        validate_modelform_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    def save(self):
        self.instance.author = self.initial['author']
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

        if should_be_approved(self.instance):
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


class CreateIncomeForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['budget', 'author']

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
        InitialValidationMixin.__init__(self)

        budget = self.initial['budget']

        self.fields['contribution'] = CreateIncomeForm.ContributionModelChoiceField(
            queryset=Contribution.objects.filter(
                fund__id=budget.fund_id).annotate(
                reserved_amount=models.Sum('incomes__amount', default=0))
            .values(
                'id', 'contribution_date',
                    'amount', 'reserved_amount'), label='Contribution')

        FormControlMixin.__init__(self)

        self.fields['budget'].widget = forms.HiddenInput()
        self.fields['reviewer'].queryset = budget.reviewers

    def save(self):
        self.instance.author = self.initial['author']
        return super().save()

    def clean(self):
        if should_be_approved(self.initial['budget']):
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


class CreateExpenseForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['budget', 'project', 'author', 'task']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['budget'].widget = forms.HiddenInput()
        self.fields['project'].widget = forms.HiddenInput()
        self.fields['amount'].initial = self.initial['task'].estimated_expense_amount
        self.fields['amount'].disabled = True
        self.fields['reviewer'].queryset = self.initial['budget'].reviewers

    task = forms.ModelChoiceField(Task.objects, disabled=True, label='Task')

    def save(self):
        self.instance.author = self.initial['author']
        self.instance.save()
        task = self.cleaned_data['task']
        task.expense = self.instance
        task.save()

        exprense_created.send(sender=Expense, instance=self.instance)

        return self.instance

    def clean(self):
        budget = self.initial['budget']
        if budget.approvement_id:
            forms.ValidationError(
                'Can not add new income record, current budget is approved')

        validate_modelform_field('task', self.initial, self.cleaned_data)

        task = self.cleaned_data['task']
        avaliable_income_amount = get_budget_available_income(budget)

        if task.estimated_expense_amount > avaliable_income_amount:
            raise forms.ValidationError(
                f'Budget avaliabe amount is {avaliable_income_amount:,.2f}. \
                Can not crate expense with amount {task.estimated_expense_amount:,.2f}')

        elif task.estimated_expense_amount <= 0:
            raise forms.ValidationError('Expense can not be empty or negative')

        return self.cleaned_data

    class Meta:
        model = Expense
        exclude = ['id', 'author',
                   'date_created', 'approvements',
                   'approvement']


class BaseApproveForm(
        forms.Form, InitialValidationMixin, FormControlMixin):
    __initial__ = ['author', 'fund', 'target']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

    is_rejected = forms.BooleanField(label='Reject', required=False)
    notes = forms.CharField(widget=forms.Textarea(),
                            label='Notes', required=False)

    def save(self):
        target = self.initial['target']

        approvement = Approvement.objects.create(
            author=self.initial['author'], fund=self.initial['fund'],
            notes=self.cleaned_data['notes'],
            is_rejected=self.cleaned_data['is_rejected'])

        target.approvement = approvement
        target.save()
        target.approvements.add(approvement)

        return target


class BudgetItemApproveForm(BaseApproveForm):
    def clean(self):
        target = self.initial['target']

        """Validate user access"""
        if not target.reviewer_id:
            raise forms.ValidationError('Reviewer is not assigned')

        if target.reviewer != self.initial['author']:
            raise forms.ValidationError(
                'Current user is not budget item reviewer')

        if not target.budget.reviewers.filter(id=self.initial['author'].id).exists():
            raise forms.ValidationError(
                'Current user is not budget reviewer, only reviewers can approve budget items')

        if should_be_approved(target.budget):
            raise forms.ValidationError(
                'Item can not be approved because budget is approved')


class ApproveBudgetForm(BaseApproveForm):
    def clean(self):
        budget = self.initial['target']

        """Validate user access"""
        if not budget.reviewers.filter(id=self.initial['author'].id).exists():
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


class AddBudgetReviewerForm(
        forms.Form, InitialValidationMixin, FormControlMixin):
    __initial__ = ['budget']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['budget'].widget = forms.HiddenInput()
        budget = self.initial['budget']
        self.fields['reviewer'].queryset = User.objects.filter(
            models.Q(volunteer_profile__fund__id=budget.fund_id) &
            ~models.Q(id__in=budget.reviewers.values('id')))

    reviewer = forms.ModelChoiceField(
        User.objects, label='Reviewer', required=True)
    budget = forms.ModelChoiceField(Budget.objects, required=True)

    def clean(self):
        validate_modelform_field('budget', self.initial, self.cleaned_data)

        if should_be_approved(self.cleaned_data['budget']):
            raise forms.ValidationError(
                'Reviewer can not be added because budget is approved')

        return self.cleaned_data

    def save(self):
        reviewer = self.cleaned_data['reviewer']
        self.initial['budget'].reviewers.add(reviewer)

        return reviewer


class EditBudgetItemForm(
        forms.Form, InitialValidationMixin, FormControlMixin):
    __initial__ = ['target', 'budget']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['reviewer'].initial = self.initial['target'].reviewer
        self.fields['notes'].initial = self.initial['target'].notes
        self.fields['reviewer'].queryset = self.initial['budget'].reviewers

    reviewer = forms.ModelChoiceField(
        User.objects, label='Reviewer', required=False)
    notes = forms.CharField(widget=forms.Textarea(),
                            label='Notes', required=False)

    def clean(self):
        reviewer = self.cleaned_data['reviewer']
        target = self.initial['target']

        if should_be_approved(target):
            raise forms.ValidationError(
                'Can not edit item because it is approved')

        if reviewer and not self.initial['budget'].reviewers.contains(reviewer):
            raise forms.ValidationError(
                'Assigned reviewer must be in list of budget reviewers')

        return self.cleaned_data

    def save(self):
        target = self.initial['target']
        target.reviewer = self.cleaned_data['reviewer']
        target.notes = self.cleaned_data['notes']

        target.save()

        if 'reviewer' in self.changed_data:
            budget_intem_reviewer_assigned.send(
                sender=target.__class__,
                budget=self.initial['budget'],
                reviewer=self.cleaned_data['reviewer'],
                instance=target)

        return target
