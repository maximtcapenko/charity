from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('<uuid:id>/details/', views.get_details, name='get_details'),
    path('<uuid:id>/edit/', views.update, name='update'),
    path('<uuid:id>/close/', views.close, name='close'),
    path('add/', views.create, name='create'),
    path('<uuid:id>/add_ward_to_project/',
         views.add_ward_to_project, name='add_ward_to_project'),
    path('<uuid:id>/add_process_to_project/',
         views.add_process_to_project, name='add_process_to_project')
]
