from django.urls import path

from . import views

app_name = "mailings"

urlpatterns = [
    path('groups', views.get_gorups_list, name='get_gorups_list'),
    path('groups/add/', views.add_group, name='add_group'),
    path('groups/<uuid:id>/remove/', views.remove_group, name='remove_group'),
    path('groups/<uuid:id>/details/',
         views.get_group_details, name='get_group_details'),
    path('groups/<uuid:id>/edit/', views.edit_group, name='edit_details'),
    path('groups/<uuid:id>/recipients/add/',
         views.add_recipient, name='add_recipient'),
    path('groups/<uuid:id>/recipients/<uuid:recipient_id>/remove/',
         views.remove_recipient, name='remove_recipient'),
    path('templates/', views.get_templates_list, name='get_templates_list'),
    path('templates/add/', views.add_template, name='add_template'),
    path('templates/<uuid:id>/edit/', views.edit_template, name='edit_template'),
    path('templates/<uuid:id>/remove/', views.remove_template, name='remove_template'),
    path('content_fields', views.get_content_type_details,
         name='get_content_type_details')
]
