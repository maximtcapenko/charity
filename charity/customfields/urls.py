from django.urls import path

from . import views

app_name = "customfields"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('add/', views.add_custom_field, name='add_custom_field'),
    path('<uuid:id>/edit/', views.edit_field_details, name='edit_field_details'),
    path('<uuid:id>/remove/', views.remove_custom_field, name='remove_custom_field')
]