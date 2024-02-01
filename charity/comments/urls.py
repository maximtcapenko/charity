from django.urls import path

from . import views

app_name = "comments"

urlpatterns = [
    path('<uuid:id>/replies/',
         views.get_replies_for_comment, name='get_replies_for_comment'),
    path('content_types/<str:model>/items/<uuid:target_id>/', views.get_comments_with_replies,
         name='get_comments_with_replies'),
    path('content_types/<str:model>/items/<uuid:id>/comments/add/',
         views.add_comment, name='add_generic_comment'),
    path('content_types/<str:model>/items/<uuid:id>/comments/<uuid:comment_id>/reply',
         views.add_reply_to_comment, name='add_reply_to_comment'),
]
