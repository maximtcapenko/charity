from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_GET

from commons import DEFAULT_PAGE_SIZE
from commons.functional import user_should_be_volunteer, wrap_dicts_page_to_objects_page
from .forms import CreateCommentForm
from .querysets import get_comments_with_reply_count_queryset
from .models import Comment


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_comment(request, model, id):
    content_type = ContentType.objects.get(model=model)
    target = content_type.get_object_for_this_type(pk=id)
    return_url = f"{reverse('%s:get_details' % content_type.app_label, args=[id])}?tab=comments"
    initial = {
        'author': request.user,
        'fund': request.user.fund,
        'target': target,
        'target_content_type': content_type
    }
    if request.method == 'GET':
        form = CreateCommentForm(initial=initial)
        form.fields['notes'].widget.attrs.update({
            'rows': 0})
    else:
        form = CreateCommentForm(request.POST, initial=initial)
        if form.is_valid():
            form.save()
            return redirect(return_url)

    return render(request, 'add_comment.html', {
        'return_url': return_url,
        'title': 'Add new topic',
        'form': form,
        'fund': request.user.fund
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_reply_to_comment(request, model, id, comment_id):
    target_content_type = ContentType.objects.get(model=model)
    target = target_content_type.get_object_for_this_type(pk=id)
    return_url = f"{reverse('%s:get_details' % target_content_type.app_label, args=[id])}?tab=comments#{comment_id}"
    comment = get_object_or_404(Comment, pk=comment_id)

    initial = {
        'author': request.user,
        'fund': request.user.fund,
        'target': target,
        'target_content_type': target_content_type,
        'reply': comment
    }
    if request.method == 'GET':
        form = CreateCommentForm(initial=initial)
        form.fields['notes'].widget.attrs.update({
            'rows': 0})
    else:
        form = CreateCommentForm(request.POST, initial=initial)
        if form.is_valid():
            form.save()
            return redirect(return_url)

    return render(request, 'add_reply.html', {
        'return_url': return_url,
        'title': 'Reply in topic',
        'form': form,
        'content_type': target_content_type,
        'target': target,
        'comment': comment,
        'fund': request.user.fund
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_GET
def get_replies_for_comment(request, comment_id):
    replies = Comment.objects.filter(reply_id=comment_id).all()
    return render(request, 'partials/comment_replies.html', {
        'replies': replies
    })


@user_passes_test(user_should_be_volunteer)
@login_required
@require_GET
def get_comments_with_replies(request, model, target_id):
    target_content_type = ContentType.objects.get(model=model)
    target = target_content_type.get_object_for_this_type(pk=target_id)
    queryset = get_comments_with_reply_count_queryset(target_content_type, target)
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)

    page = wrap_dicts_page_to_objects_page(
        paginator.get_page(request.GET.get('page')), model=Comment)

    return render(request, 'partials/comments.html', {
        'content_type': target_content_type,
        'target': target,
        'items_count': paginator.count,
        'page': page
    })
