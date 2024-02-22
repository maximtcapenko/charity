from django.contrib.contenttypes.models import ContentType
from django.db.models import Count

from commons.functional import resolve_many_2_many_attr_path

from .models import Comment


def get_comments_with_reply_count_queryset(target_content_type, target):
    """
    Returns projection: {
    `'id'`, `'author__id'`, `'author__username'`, `'author__volunteer_profile__cover'`,
    `author__volunteer_profile__id`, `'date_created'`, `'notes'`, `'replies_count'` }
    """
    attr_path = resolve_many_2_many_attr_path(Comment, target_content_type.model_class())
    comments = getattr(target, attr_path)

    return comments.filter(
        reply_id__isnull=True).annotate(
        replies_count=Count('replies')).values(
        'id', 'author__id', 'author__username', 'author__volunteer_profile__id', 'author__volunteer_profile__cover',
        'date_created', 'notes', 'replies_count').order_by('date_created')
