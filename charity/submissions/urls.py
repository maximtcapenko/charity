from django.urls import path

from . import views

app_name = "submissions"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('add/', views.add_submission, name='add_submission'),
    path('<uuid:id>/details/', views.get_submission_details, name='get_submission_details'),
    path('<uuid:id>/edit/', views.edit_submission, name='edit_submission'),
    path('<uuid:id>/remove/', views.remove_submission, name='remove_submission'),
    path('<uuid:id>/add_ward/', views.add_submission_ward, name='add_submission_ward'),
    path('<uuid:id>/wards/<uuid:ward_id>/remove', views.remove_submission_ward, name='remove_submission_ward'),
    path('<uuid:id>/send/', views.send_submission, name='send_submission')
]
