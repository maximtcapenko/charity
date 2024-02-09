import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from commons.models import Notification
from funds.models import Contributor, Contribution, Fund

from .models import Budget, Income
from .requirements import user_should_be_budget_item_reviewer, \
    user_should_be_budget_item_editor, user_should_be_budget_owner


class BudgetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.budget_author = User.objects.create_user('budget_author')
        cls.budget_manager = User.objects.create_user('budget_manager')
        cls.budget_reviewer = User.objects.create_user('budget_reviewer')

        current_fund = Fund.objects.create(name=get_random_string(20))
        cls.current_budget = Budget.objects.create(
            name=get_random_string(20),
            author=cls.budget_author,
            manager=cls.budget_manager,
            fund=current_fund)
        cls.current_budget.reviewers.add(cls.budget_reviewer)
        contributor = Contributor.objects.create(
            is_company=False,
            fund=current_fund, name=get_random_string(20))
        contribution = Contribution.objects.create(
            contribution_date=datetime.datetime.utcnow(),
            fund=current_fund, contributor=contributor, amount=1000, author=cls.budget_author)
        cls.income = Income.objects.create(
            amount=1000,
            budget=cls.current_budget, contribution=contribution,
            author=cls.budget_author, reviewer=cls.budget_reviewer)

    def test_budget_manager_should_be_default_reviewer(self):
        reviewers = self.current_budget.reviewers.all()
        self.assertIn(self.budget_manager, reviewers)

        notifications = self.budget_manager.notifications.filter(
            short='Role assignment').all()
        self.assertTrue(len(notifications) > 0)

    def test_notification_generated_for_income_reviewer_and_budget_manager(self):
        self.assertTrue(Notification.objects.filter(
            receiver__in=[self.budget_manager, self.budget_reviewer]).exists())

    def test_income_or_expense_requirement(self):
        '''Budget items reviewer tests (reviewer can approve incomes or expenses)'''
        self.assertTrue(user_should_be_budget_item_reviewer(
            self.budget_manager, self.income))
        self.assertTrue(user_should_be_budget_item_reviewer(
            self.budget_reviewer, self.income))

        '''Budget item editor tests (editor can create, edit and delete incomes or expenses)'''
        self.assertTrue(user_should_be_budget_item_editor(
            self.budget_author, self.income))
        self.assertTrue(user_should_be_budget_item_editor(
            self.budget_manager, self.income))
        self.assertTrue(user_should_be_budget_item_editor(
            self.budget_reviewer, self.income))

    def test_budget_edit_requirement(self):
        '''Budget owner tests (can delete budget)'''
        self.assertTrue(user_should_be_budget_owner(
            self.budget_author, self.current_budget))
        self.assertTrue(user_should_be_budget_owner(
            self.budget_manager, self.current_budget))
