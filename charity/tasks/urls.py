from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path('<uuid:id>/edit/', views.update, name='update'),
    path('<uuid:id>/details/', views.get_details, name='get_details'),
    path('add/', views.create, name='create'),
    path('<uuid:id>/comments/add', views.add_comment, name='add_comment'),
    path('comments/<uuid:id>/details', views.get_comment_details, name='get_comment_details')
]
