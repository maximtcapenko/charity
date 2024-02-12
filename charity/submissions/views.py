from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_GET

from commons import DEFAULT_PAGE_SIZE
from commons.functional import user_should_be_volunteer, render_generic_form

from .forms import AddSubmissionForm
from .models import Submission


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_list(request):
    paginator = Paginator(Submission.objects.filter(
        fund=request.user.fund), DEFAULT_PAGE_SIZE)
    return render(request, 'submissions_list.html', {
        'items_count': paginator.count,
        'page': paginator.get_page(request.GET.get('page')),
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_submission(request):
    return render_generic_form(request, form_class=AddSubmissionForm, context={
        'title': 'Add submission',
        'return_url': reverse('submissions:get_list'),
        'initial':{
            'fund': request.user.fund,
            'author': request.user
        }
    })
