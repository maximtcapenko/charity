from django.urls import path

from . import views

app_name = "budgets"

urlpatterns = [
    path('add', views.create, name='create'),
    path('', views.get_list, name='get_list'),
    path('<uuid:id>/details/', views.get_details, name='get_details'),
    path('<uuid:id>/expenses_planing/',
         views.budget_expenses_planing, name='expenses_planing'),
    path('<uuid:id>/expenses/add/', views.add_budget_expenses, name='add_expenses'),
    path('<uuid:id>/incomes/add/', views.create_budget_income, name='add_income'),
    path("incomes/<uuid:id>/details/",
         views.get_income_details, name="get_income_details"),
    path('expenses/<uuid:id>/details/',
         views.get_expense_details, name='get_expense_details'),
    path('incomes/<uuid:id>/approvements/add/',
         views.approve_budget_income, name='approve_budget_income'),
    path('expenses/<uuid:id>/approvements/add/',
         views.approve_budget_expense, name='approve_budget_expense'),
    path('<uuid:id>/approve_budget/', views.approve_budget, name='approve_budget')
]
