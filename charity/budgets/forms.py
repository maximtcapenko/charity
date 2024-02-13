import datetime

from django import forms
from django.contrib.auth.models import User
from django.db import models

from commons.mixins import InitialMixin, FormControlMixin, SearchByNameMixin
from commons.functional import validate_modelform_field, should_be_approved
from commons.forms import ApprovedOnlySearchForm, user_model_choice_field

from funds.models import Approvement, Contributor
from funds.forms import CreateContributionForm
from tasks.models import Expense, Task

from .functional import get_budget_available_income
from .messages import Warnings
from .models import Budget, Income, Contribution
from .signals import exprense_created, budget_item_reviewer_assigned


class CreateBudgetForm(
        forms.ModelForm, InitialMixin, FormControlMixin):
    __initial__ = ['fund', 'author']
    field_order = ['name', 'manager']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.fund.widget = forms.HiddenInput()
        self.form.manager = user_model_choice_field(
            fund=self.fund, label='Manager')

        FormControlMixin.__init__(self, *args, **kwargs)

    def clean(self):
        validate_modelform_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    def save(self):
        self.instance.author = self.author
        return super().save()

    class Meta:
        model = Budget
        exclude = ['id', 'date_creted', 'closed_date',
                   'author', 'is_closed', 'payout_excess_contribution',
                   'approvement', 'approvements', 'reviewers']


class UpdateBudgetForm(CreateBudgetForm):
    def clean(self):
        if self.instance.is_closed:
            raise forms.ValidationError(
                Warnings.BUDGET_CANNOT_BE_CHANGED_IT_HAS_BEEN_CLOSED)

        if should_be_approved(self.instance):
            raise forms.ValidationError(
                Warnings.BUDGET_CANNOT_BE_CHANGED_IT_HAS_BEEN_APPROVED)

        validate_modelform_field('fund', self.initial, self.cleaned_data)
        return self.cleaned_data

    def clean_manager(self):
        manager = self.cleaned_data['manager']
        if manager is None and self.instance.manager:
            raise forms.ValidationError(
                Warnings.BUDGET_MANAGER_CANNOT_BE_UNDEFINED)
        return manager


class SearchBudgetForm(ApprovedOnlySearchForm, SearchByNameMixin):
    def __init__(self, fund, *args, **kwargs):
        super().__init__(*args, **kwargs)
        SearchByNameMixin.__init__(self)

        self.fields['manager'].queryset = User.objects.filter(
            models.Q(volunteer_profile__fund=fund)
            & models.Exists(Budget.objects.filter(fund=fund, manager=models.OuterRef('pk'))))
        self.fields['manager'].widget.attrs.update({
            'onchange': 'javascript:this.form.submit()'
        })
        self.order_fields(['approved_only', 'name'])
        self.__resolvers__['manager'] = lambda field: models.Q(manager=field)

    manager = forms.ModelChoiceField(queryset=User.objects, label='Manager')


class CreatePayoutExcessContributionForm(CreateContributionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.form.amount.disabled = True
        self.fields.pop('contribution_date')
        self.form.contributor.queryset = Contributor.objects \
            .filter(fund=self.fund, is_internal=True)

    def save(self):
        self.instance.contribution_date = datetime.datetime.utcnow()
        contribution = super().save()

        self.budget.payout_excess_contribution = contribution
        self.budget.save()

        return self.budget


class CreateIncomeForm(
        forms.ModelForm, InitialMixin, FormControlMixin):
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
            amount = obj['amount'] - obj['reserved_amount']
            return '%s - %s (%s)' % (
                obj['contribution_date'].strftime('%b. %d, %Y'),
                obj['contributor__name'], "{:2,}".format(amount))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.contribution = CreateIncomeForm.ContributionModelChoiceField(
            queryset=Contribution.objects.filter(
                fund__id=self.budget.fund_id).annotate(
                reserved_amount=models.Sum('incomes__amount', default=0))
            .annotate(avaliable_amount=models.ExpressionWrapper(
                models.F('amount') - models.F('reserved_amount'),
                output_field=models.DecimalField()))
            .filter(avaliable_amount__gt=0)
            .order_by('contribution_date')
            .values('id', 'contributor__name', 'contribution_date',
                    'amount', 'reserved_amount'), label='Contribution')

        self.form.budget.widget = forms.HiddenInput()
        self.form.reviewer = user_model_choice_field(
            queryset=self.budget.reviewers, label='Reviewer')

        FormControlMixin.__init__(self)

    def save(self):
        self.instance.author = self.author
        return super().save()

    def clean(self):
        if should_be_approved(self.budget):
            forms.ValidationError(
                Warnings.INCOME_CANNOT_BE_ADDED_BUDGET_HAS_BEEN_APPROVED)

        contribution = self.cleaned_data['contribution']
        amount = self.cleaned_data['amount']
        reserved_amount = contribution.incomes.aggregate(
            total=models.Sum('amount', default=0))['total']

        if (contribution.amount - reserved_amount) < amount:
            raise forms.ValidationError(Warnings.NO_CONTIBUTION)
        elif amount <= 0:
            raise forms.ValidationError(Warnings.INCOME_SHOULD_BE_POSITIVE)

        return self.cleaned_data

    class Meta:
        model = Income
        exclude = ['id', 'author',
                   'date_created', 'approvements',
                   'approvement']


class CreateExpenseForm(
        forms.ModelForm, InitialMixin, FormControlMixin):
    __initial__ = ['budget', 'project', 'author', 'task']

    field_order = ['task', 'amount', 'reviewer', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.budget.widget = forms.HiddenInput()
        self.form.project.widget = forms.HiddenInput()
        self.form.amount.initial = self.task.estimated_expense_amount
        self.form.amount.disabled = True
        self.form.reviewer = user_model_choice_field(
            queryset=self.budget.reviewers, label='Reviewer')

        FormControlMixin.__init__(self)

    task = forms.ModelChoiceField(Task.objects, disabled=True, label='Task')

    def save(self):
        self.instance.author = self.author
        self.instance.save()
        task = self.cleaned_data['task']
        task.expense = self.instance
        task.save()

        exprense_created.send(sender=Expense, instance=self.instance)

        return self.instance

    def clean(self):
        budget = self.budget
        if budget.approvement_id:
            forms.ValidationError(
                Warnings.EXPENSE_CANNOT_BE_ADDED_BUDGET_HAS_BEEN_APPROVED)

        validate_modelform_field('task', self.initial, self.cleaned_data)

        task = self.cleaned_data['task']
        avaliable_income_amount = get_budget_available_income(budget)

        if task.estimated_expense_amount > avaliable_income_amount:
            raise forms.ValidationError(
                f'Budget avaliabe amount is {avaliable_income_amount:,.2f}. \
                Can not create expense with amount {task.estimated_expense_amount:,.2f}')

        elif task.estimated_expense_amount <= 0:
            raise forms.ValidationError(Warnings.EXPENSE_SHOULD_BE_POSITIVE)

        return self.cleaned_data

    class Meta:
        model = Expense
        exclude = ['id', 'author',
                   'date_created', 'approvements',
                   'approvement']


class BaseApproveForm(
        forms.Form, InitialMixin, FormControlMixin):
    __initial__ = ['author', 'fund', 'target']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)
        FormControlMixin.__init__(self)

    is_rejected = forms.BooleanField(label='Reject', required=False)
    notes = forms.CharField(widget=forms.Textarea(),
                            label='Notes', required=False)

    def clean(self):
        target = self.target
        if should_be_approved(target):
            '''TODO: make more complex validation 
            - if budget amount already used in planing, etc'''
            raise forms.ValidationError(
                Warnings.BUDGET_ITEM_HAS_BEEN_ALREADY_APPROVED)

        return self.cleaned_data

    def save(self):
        approvement = Approvement.objects.create(
            author=self.author, fund=self.fund,
            notes=self.cleaned_data['notes'],
            is_rejected=self.cleaned_data['is_rejected'])

        self.target.approvement = approvement
        self.target.save()
        self.target.approvements.add(approvement)

        return self.target


class BudgetItemApproveForm(BaseApproveForm):
    def clean(self):
        """Validate user access"""
        if not self.target.reviewer_id:
            raise forms.ValidationError(Warnings.BUDGET_REVIEWER_NOT_ASSIGNED)

        if self.target.reviewer == self.author and \
                not self.target.budget.reviewers.filter(id=self.author.id).exists():
            raise forms.ValidationError(
                Warnings.CURRENT_USER_IS_NOT_BUDGET_ITEM_REVIEWER)

        if should_be_approved(self.target.budget):
            raise forms.ValidationError(
                Warnings.BUDGET_CANNOT_BE_CHANGED_IT_HAS_BEEN_APPROVED)


class ApproveBudgetForm(BaseApproveForm):
    def clean(self):
        budget = self.target

        """Validate user access"""
        if not budget.reviewers.filter(id=self.author.id).exists():
            raise forms.ValidationError(
                Warnings.CURRENT_USER_IS_NOT_BUDGET_REVIEWER)

        incomes = budget.incomes.exists()
        expenses = budget.expenses.exists()

        if incomes == False or expenses == False:
            raise forms.ValidationError(
                Warnings.BUDGET_CANNOT_BE_APPROVED_NO_BUDGET_ITEMS)

        unapproved_incomes = budget.incomes.filter(
            approvement_id__isnull=True).exists()

        unapproved_expenses = budget.expenses.filter(
            approvement_id__isnull=True).exists()

        if unapproved_incomes or unapproved_expenses:
            raise forms.ValidationError(
                Warnings.BUDGET_CANNOT_BE_APPROVED_NO_APPROVED_BUDGET_ITEMS)

        return self.cleaned_data


class AddBudgetReviewerForm(
        forms.Form, InitialMixin, FormControlMixin):
    __initial__ = ['budget']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.budget.widget = forms.HiddenInput()
        self.form.reviewer = user_model_choice_field(queryset=User.objects.filter(
            models.Q(volunteer_profile__fund=self.budget.fund) &
            ~models.Q(id__in=self.budget.reviewers.values('id'))), label='Reviewer')

        FormControlMixin.__init__(self)

    budget = forms.ModelChoiceField(Budget.objects, required=True)

    def clean(self):
        validate_modelform_field('budget', self.initial, self.cleaned_data)

        if should_be_approved(self.cleaned_data['budget']):
            raise forms.ValidationError(
                Warnings.BUDGET_CANNOT_BE_CHANGED_IT_HAS_BEEN_APPROVED)

        return self.cleaned_data

    def save(self):
        reviewer = self.cleaned_data['reviewer']
        self.budget.reviewers.add(reviewer)

        return reviewer


class EditBudgetItemForm(
        forms.Form, InitialMixin, FormControlMixin):
    __initial__ = ['target', 'budget']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.notes.initial = self.target.notes
        self.form.reviewer = user_model_choice_field(
            queryset=self.budget.reviewers, label='Reviewer', initial=self.target.reviewer)

        FormControlMixin.__init__(self)

    reviewer = forms.ModelChoiceField(
        User.objects, label='Reviewer', required=False)
    notes = forms.CharField(widget=forms.Textarea(),
                            label='Notes', required=False)

    def clean(self):
        reviewer = self.cleaned_data['reviewer']
        if should_be_approved(self.target):
            raise forms.ValidationError(
                Warning.BUDGET_ITEM_CANNOT_BE_CHANGED_IT_HAS_BEEN_APPROVED)

        if reviewer and not self.budget.reviewers.contains(reviewer):
            raise forms.ValidationError(
                Warnings.CURRENT_USER_IS_NOT_BUDGET_REVIEWER)

        return self.cleaned_data

    def save(self):
        self.target.reviewer = self.cleaned_data['reviewer']
        self.target.notes = self.cleaned_data['notes']

        self.target.save()

        if 'reviewer' in self.changed_data:
            budget_item_reviewer_assigned.send(
                sender=self.target.__class__,
                budget=self.budget,
                reviewer=self.cleaned_data['reviewer'],
                instance=self.target)

        return self.target
