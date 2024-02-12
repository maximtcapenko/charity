from django.urls import path

from . import views

app_name = "submissions"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('add/', views.add_submission, name='add_submission')
]
