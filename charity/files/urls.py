from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    path('<uuid:id>/', views.get_file, name='get_file'),
]
