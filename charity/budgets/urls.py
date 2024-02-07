from django.urls import path

from . import views

app_name = "budgets"

urlpatterns = [
    path('add', views.add_budget, name='create'),
    path('', views.get_projects_list, name='get_list'),
    path('<uuid:id>/details/', views.get_budget_details, name='get_details'),
    path('<uuid:id>/edit/', views.edit_details, name='edit_details'),
    path('<uuid:id>/remove/', views.remove_budget, name='remove'),
    path('<uuid:id>/excess_contributions/add/',
         views.add_budget_excess_contribution, name="add_budget_excess_contribution"),
    path('<uuid:id>/expenses_planing/',
         views.budget_expenses_planing, name='expenses_planing'),
    path('<uuid:id>/expenses/add/', views.add_budget_expense, name='add_expenses'),
    path('<uuid:id>/incomes/add/', views.add_budget_income, name='add_income'),
    path("<uuid:id>/incomes/<uuid:income_id>/details/",
         views.get_income_details, name="get_income_details"),
    path('<uuid:id>/expenses/<uuid:expense_id>/details/',
         views.get_expense_details, name='get_expense_details'),
    path('<uuid:id>/incomes/<uuid:income_id>/approvements/add/',
         views.approve_budget_income, name='approve_budget_income'),
    path('<uuid:id>/expenses/<uuid:expense_id>/approvements/add/',
         views.approve_budget_expense, name='approve_budget_expense'),
    path('<uuid:id>/approve/', views.approve_budget, name='approve_budget'),
    path('<uuid:id>/reviewers/add/', views.add_budget_reviewer,
         name='add_budget_reviewer'),
    path('<uuid:id>/reviewers/<int:reviewer_id>/remove/',
         views.remove_budget_reviewer, name='remove_budget_reviewer'),
    path('<uuid:id>/reviewers/<int:reviewer_id>/details/',
         views.get_reviewer_details, name='get_reviewer_details'),
    path('<uuid:id>/expenses/<uuid:expense_id>/remove/',
         views.remove_budget_expense, name='remove_budget_expense'),
    path('<uuid:id>/incomes/<uuid:income_id>/remove/',
         views.remove_budget_income, name='remove_budget_income'),
    path('<uuid:id>/incomes/<uuid:income_id>/edit/',
         views.edit_budget_income_details, name='edit_income_details'),
    path('<uuid:id>/expenses/<uuid:expense_id>/edit/',
         views.edit_budget_expense_details, name='edit_expense_details'),
]
