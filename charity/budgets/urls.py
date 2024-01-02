from django.urls import path

from . import views

app_name = "budgets"

urlpatterns = [
    path('add', views.create, name='create'),
    path('', views.get_list, name='get_list'),
    path('<uuid:id>/details/', views.get_details, name='get_details'),
    path('<uuid:id>/incomes/add', views.create_budget_income, name='add_income'),
    path("incomes/<uuid:id>/details", views.get_income_details, name="get_income_details")
]
