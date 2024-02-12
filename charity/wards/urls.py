from django.urls import path

from . import views

app_name = "wards"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('<uuid:id>/', views.get_details, name='get_details'),
    path('<uuid:id>/cover/', views.add_ward_cover, name='add_ward_cover'),
    path('create/', views.create, name='create'),
    path('<uuid:id>/edit/', views.edit_details, name='edit_details'),
]