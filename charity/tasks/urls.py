from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('<uuid:id>/update/', views.update, name='update'),
    path('<uuid:id>/', views.get_details, name='get_details'),
    path('create/', views.create, name='create')
]
