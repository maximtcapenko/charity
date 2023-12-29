from django.urls import path

from . import views

app_name = "processes"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('create/', views.create, name='create'),
    path('<uuid:id>/', views.get_details, name='get_details'),
    path('<uuid:id>/create_state', views.create_state, name='create_state')
]
