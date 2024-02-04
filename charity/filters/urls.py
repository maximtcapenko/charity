from django.urls import path

from . import views

app_name = "filters"

urlpatterns = [
    path('<str:model_name>', views.get_list, name='get_list'),
    path('<str:model_name>/add/', views.add_filter, name='add_filter'),
    path('<uuid:id>/details/', views.get_filter_details, name='get_details'),
    path('<uuid:id>/edit/', views.edit_filter_details, name='edit_details'),
    path('<uuid:id>/remove/', views.remove_filter, name='remove_filter'),
    path('<uuid:id>/expressions/add/', views.add_expression, name='add_expression'),
    path('<uuid:id>/expressions/<uuid:expression_id>/details/', views.get_expression_details, name='get_expression_details'),
    path('<uuid:id>/expressions/<uuid:expression_id>/remove/', views.remove_expression, name='remove_expression'),
    path('<uuid:id>/expressions/<uuid:expression_id>/add_value', views.add_expression_value, name='add_expression_value'),
    path('customfields/', views.get_filed_value_input_details, name='get_filed_value_input_details')
]