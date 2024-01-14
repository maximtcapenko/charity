from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('<uuid:id>/details/', views.get_details, name='get_details'),
    path('<uuid:id>/edit/', views.edit_details, name='update'),
    path('<uuid:id>/close/', views.close, name='close'),
    path('add/', views.create, name='create'),
    path('<uuid:id>/add_ward_to_project/', views.add_ward_to_project, name='add_ward_to_project'),
    path('<uuid:id>/add_process_to_project/', views.add_process_to_project, name='add_process_to_project'),
    path('<uuid:id>/reviewers/add/', views.add_project_reviewer, name='add_project_reviewer'),
    path('<uuid:id>/reviewers/<int:reviewer_id>/remove/', views.remove_project_reviewer, name='remove_project_reviewer'),
    path('<uuid:id>/reviewers/<int:reviewer_id>/details', views.get_reviewer_details, name='get_reviewer_details'),
    path('<uuid:id>/processes/<uuid:process_id>/remove/', views.remove_project_process, name='remove_project_process'),
    path('<uuid:id>/wards/<uuid:ward_id>/remove/', views.remove_project_ward, name='remove_project_ward'),
    path('<uuid:id>/tasks/<uuid:task_id>/remove/', views.remove_project_task, name='remove_project_task')
]
