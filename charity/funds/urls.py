from django.urls import path

from . import views

app_name = "funds"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('<uuid:id>', views.get_details, name='get_details'),
    path('index/',views.get_current_details, name='get_current_details'),
    path("<uuid:id>/update", views.update_details, name="update_details")
]
