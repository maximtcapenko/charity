"""
URL configuration for charity project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, reverse
from django.contrib.auth import views as auth_views

from commons import views as common_views

urlpatterns = [
    path("accounts/login/", auth_views.LoginView.as_view(template_name="login.html")),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page='funds:get_current_details'), name='logout'),
    path('admin/', admin.site.urls),
    path('budgets/', include('budgets.urls')),
    path('comments/', include('comments.urls')),
    path('customfields/', include('customfields.urls')),
    path('files/', include('files.urls')),
    path('filters/', include('filters.urls')),
    path('funds/', include('funds.urls')),
    path('notifications/<uuid:id>/details/',
         common_views.view_notification_details, name='view_notification_details'),
    path('processes/', include('processes.urls')),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('wards/', include('wards.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
