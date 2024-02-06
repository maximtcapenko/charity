from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path('add/', views.add_task, name='create'),
    path('<uuid:id>/edit/', views.edit_details, name='edit_details'),
    path('<uuid:id>/details/', views.get_details, name='get_details'),
    path('<uuid:id>>/complete/', views.complete_task, name='complete_task'),
    path('<uuid:task_id>/states/<uuid:id>/details/', views.get_state_details, name='get_state_details'),
    path('<uuid:task_id>/states/<uuid:id>/approve/',views.approve_task_state, name='approve_task_state'),
    path('<uuid:task_id>/states/<uuid:id>/request_review/',views.request_task_state_review, name='request_task_state_review'),
    path('<uuid:id>/start_next_state/', views.start_next_state, name='move_to_next_state')
]
