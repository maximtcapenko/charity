from django.urls import path

from . import views

app_name = "wards"

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('<uuid:id>/', views.get_details, name='get_details')
]