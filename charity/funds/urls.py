from django.urls import path

from . import views

app_name = "funds"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('<uuid:id>/details/', views.get_details, name='get_details'),
    path('index/partial/', views.get_get_current_details_partial, name='get_get_current_details_partial'),
    path('index/',views.get_current_details, name='get_current_details'),
    path('index/volunteers/<uuid:id>/details/', views.get_volunteer_details, name='get_volunteer_details'),
    path('index/contributions/add/', views.add_contribution, name='add_contribution'),
    path('index/contributions/<uuid:id>/details', views.get_contribution_details, name='get_contribution_details'),
    path('index/volunteers/add/', views.add_volunteer, name='add_volunteer'),
    path('index/volunteers/<uuid:id>/edit/', views.edit_volunteer_profile, name='edit_volunteer_profile'),
    path('index/volunteers/<uuid:id>/cover/', views.add_volunteer_cover, name='add_volunteer_cover'),
    path('index/contributors/add/', views.add_contributor, name='add_contributor'),
    path('index/contributors/<uuid:id>/details/', views.get_contributor_details, name='get_contributor_details'),
    path('index/contributors/<uuid:id>/edit/', views.edit_contributor_details, name='edit_contributor_details')
]
