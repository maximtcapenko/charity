from django.contrib.contenttypes.models import ContentType
from django.db.models import Count

from commons.models import Comment

from .functions import resolve_many_2_many_attr


def get_comments_with_reply_count_queryset(model: str, pk):
    """
    Returns projection: {
    `'id'`, `'author__id'`, `'author__username'`, `'author__volunteer_profile__cover'`,
    `author__volunteer_profile__id`, `'date_created'`, `'notes'`, `'replies_count'` }
    """
    content_type = ContentType.objects.get(model=model)
    comments = resolve_many_2_many_attr(Comment, content_type, pk)

    return comments.filter(
        reply_id__isnull=True).annotate(
        replies_count=Count('replies')).values(
        'id', 'author__id', 'author__username', 'author__volunteer_profile__id', 'author__volunteer_profile__cover',
        'date_created', 'notes', 'replies_count').order_by('date_created')
