from django.urls import path

from . import views

app_name = "funds"

urlpatterns = [
    path('', views.get_list, name='funds_list'),
    path('<uuid:id>', views.get_details, name='fund_details'),
    path('index/',views.get_current_details, name='current_fund_details'),
    path("<uuid:id>/update", views.update_details, name="fund_update_details")
]
