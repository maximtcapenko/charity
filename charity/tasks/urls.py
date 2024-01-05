from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path('<uuid:id>/edit/', views.edit_details, name='update'),
    path('<uuid:id>/details/', views.get_details, name='get_details'),
    path('add/', views.create, name='create'),
    path('<uuid:id>/comments/add', views.add_comment, name='add_comment'),
    path('comments/<uuid:id>/details/', views.get_comment_details, name='get_comment_details'),
    path('<uuid:task_id>/states/<uuid:id>/details/', views.get_state_details, name='get_state_details'),
    path('<uuid:task_id>/states/<uuid:id>/approve/',views.approve_task_state, name='approve_task_state'),
    path('<uuid:id>/move_to_next_state/', views.move_to_next_state, name='move_to_next_state')
]
