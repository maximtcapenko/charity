from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from commons import DEFAULT_PAGE_SIZE
from commons.exceptions import ApplicationError
from commons.functional import resolve_many_2_many_attr, resolve_many_2_many_attr_path, \
    user_should_be_volunteer, render_generic_form

from .forms import CreateAttachmentForm
from .models import Attachment
from .requirements import file_is_ready_to_be_removed, file_is_ready_to_be_added


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def attach_file(request, model, target_id):
    content_type = ContentType.objects.get(model=model)
    target = content_type.get_object_for_this_type(pk=target_id)
    return_url = f'{target.url}?tab=files'
    
    if not file_is_ready_to_be_added(target, content_type):
        raise ApplicationError('File cannot be attached.', return_url)

    initial = {
        'author': request.user,
        'fund': request.user.fund,
        'target': target,
        'target_content_type': content_type
    }
    return render_generic_form(
        request=request,
        form_class=CreateAttachmentForm,
        context={
            'return_url': return_url,
            'title': 'Upload file',
            'initial': initial
        })


@user_passes_test(user_should_be_volunteer)
@require_POST
def remove_file(request, id, model, target_id):
    content_type = ContentType.objects.get(model=model)
    target = content_type.get_object_for_this_type(pk=target_id)
    return_url = f'{target.url}?tab=files'
    
    files = resolve_many_2_many_attr(Attachment, content_type, target_id)
    file = get_object_or_404(files, pk=id)
    if not file_is_ready_to_be_removed(file, target, content_type):
        raise ApplicationError('File cannot be removed.', return_url)

    file.delete()

    return redirect(return_url)

@user_passes_test(user_should_be_volunteer)
@require_POST
def change_file_access(request, id, model, target_id):
    content_type = ContentType.objects.get(model=model)
    files = resolve_many_2_many_attr(Attachment, content_type, target_id)
    file = get_object_or_404(files, pk=id)
    file.is_public = not file.is_public

    return HttpResponse()

@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def get_list(request, model, target_id):
    content_type = ContentType.objects.get(model=model)
    target = content_type.get_object_for_this_type(pk=target_id)
    target_attr = resolve_many_2_many_attr_path(
        Attachment, content_type.model_class())
    files = getattr(target, target_attr)

    paginator = Paginator(files.select_related(
        'author',
        'author__volunteer_profile'
    ).order_by('date_created'), DEFAULT_PAGE_SIZE)

    return render(request, 'partials/files_list.html', {
        'page': paginator.get_page(request.GET.get('page')),
        'content_type': content_type,
        'target': target,
        'items_count': paginator.count,
    })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_file(request, id):
    file = get_object_or_404(Attachment, pk=id)
    return FileResponse(file.file, as_attachment=True, filename=file.file.name)
