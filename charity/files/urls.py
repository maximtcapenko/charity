from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    path('<uuid:id>/', views.get_file, name='get_file'),
    path('content_types/<str:model>/items/<uuid:target_id>/attach/', views.attach_file, name='attach_file')
]
