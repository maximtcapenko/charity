from django.urls import path

from . import views

app_name = "wards"

urlpatterns = [
    path('', views.get_list, name='wards_list'),
    path('<uuid:id>/', views.get_details, name='ward_details'),
    path('create/', views.create, name='ward_create')
]