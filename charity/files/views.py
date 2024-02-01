from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from commons import DEFAULT_PAGE_SIZE
from commons.functions import resolve_many_2_many_attr, user_should_be_volunteer, render_generic_form

from .forms import CreateAttachmentForm
from .models import Attachment


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def attach_file(request, model, target_id):
    content_type = ContentType.objects.get(model=model)
    return_url = f"{reverse('%s:get_details' % content_type.app_label, args=[target_id])}?tab=files"
    initial = {
        'author': request.user,
        'fund': request.user.volunteer_profile.fund,
        'target_id': target_id,
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
@require_http_methods(['GET', 'POST'])
def get_list(request, model, target_id):
    content_type = ContentType.objects.get(model=model)
    files = resolve_many_2_many_attr(Attachment, content_type, target_id)
    paginator = Paginator(files.select_related(
        'author',
        'author__volunteer_profile'
    ).order_by('date_created'), DEFAULT_PAGE_SIZE)

    return render(request, 'partials/files_list.html', {
        'page': paginator.get_page(request.GET.get('page')),
        'items_count': paginator.count,
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_file(request, id):
    file = get_object_or_404(Attachment, pk=id)
    return FileResponse(file.file, as_attachment=True, filename=file.name)
