from django.urls import path

from . import views

app_name = "histories"

urlpatterns = [
    path('', views.get_list, name='get_list'),
]