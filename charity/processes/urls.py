from django.urls import path

from . import views

app_name = "processes"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('add/', views.create, name='create'),
    path('<uuid:id>/edit/', views.edit_details, name='edit_details'),
    path('<uuid:id>/details/', views.get_details, name='get_details'),
    path('<uuid:id>/create_state', views.create_state, name='create_state')
]
