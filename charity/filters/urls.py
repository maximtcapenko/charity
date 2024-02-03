from django.urls import path

from . import views

app_name = "filters"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('add/', views.add_filter, name='add_filter'),
    path('<uuid:id>/details/', views.get_details, name='get_details'),
    path('<uuid:id>/expressions/add/', views.add_expression, name='add_expression'),
    path('<uuid:id>/expressions/<uuid:expression_id>/remove/', views.remove_expression, name='remove_expression'),
    path('customfields/', views.get_filed_value_input_details, name='get_filed_value_input_details')
]