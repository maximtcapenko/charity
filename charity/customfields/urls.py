from django.urls import path

from . import views

app_name = "customfields"

urlpatterns = [
    path('', views.get_fields_configuration, name='get_fields_configuration'),
    path('add/', views.add_custom_field, name='add_custom_field'),
    path('<uuid:id>/edit/', views.edit_custom_field, name='edit_custom_field')
]