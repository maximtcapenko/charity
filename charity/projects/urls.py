from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path('', views.get_list, name='projects_list'),
    path('<uuid:id>/', views.get_details, name='project_details'),
    path('create/', views.create, name='project_create')
]
