from django.apps import AppConfig


class BudgetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budgets'

    def ready(self):
        from .signals import add_default_reviewers,\
              budget_income_added, budget_expense_added,\
              budget_income_approved, budget_expense_approved
        return super().ready()
