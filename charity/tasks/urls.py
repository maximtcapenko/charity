from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path('', views.get_list, name='tasks_list'),
    path('<uuid:id>/', views.get_details, name='get_details')
]