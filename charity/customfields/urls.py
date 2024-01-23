from django.urls import path

from . import views

app_name = "customfields"

urlpatterns = [
    path('', views.get_fields_configuration, name='get_fields_configuration'),
]