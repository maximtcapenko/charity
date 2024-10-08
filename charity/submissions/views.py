from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from commons import DEFAULT_PAGE_SIZE
from commons.exceptions import ApplicationError
from commons.functional import user_should_be_volunteer, render_generic_form

from wards.forms import AttachWardToTargetForm

from .forms import AddSubmissionForm
from .models import Submission
from .requirements import submission_can_be_edited
from .tasks import send_submssions


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_list(request):
    paginator = Paginator(
        Submission.objects
        .select_related('mailing_template', 'mailing_group', 'author__volunteer_profile').filter(
            fund=request.user.fund), DEFAULT_PAGE_SIZE)
    return render(request, 'submissions_list.html', {
        'title': 'Submissions',
        'items_count': paginator.count,
        'page': paginator.get_page(request.GET.get('page')),
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_submission(request):
    return render_generic_form(request, form_class=AddSubmissionForm, context={
        'title': 'Add submission',
        'return_url': reverse('submissions:get_list'),
        'initial': {
            'fund': request.user.fund,
            'author': request.user
        }
    })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_submission_details(request, id):
    submission = get_object_or_404(
        Submission.objects.filter(fund=request.user.fund), pk=id)
    paginator = Paginator(submission.wards.all(), DEFAULT_PAGE_SIZE)
    return render(request, 'submission_details.html', {
        'submission': submission,
        'items_count': paginator.count,
        'page': paginator.get_page(request.GET.get('page')),
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_submission(request, id):
    submission = get_object_or_404(
        Submission.objects.filter(fund=request.user.fund), pk=id)

    return_url = reverse('submissions:get_submission_details', args=[id])
    if not submission_can_be_edited(submission, request.user):
        raise ApplicationError('Submission cannot be edited.', return_url)

    return render_generic_form(request, form_class=AddSubmissionForm, context={
        'title': 'Edit submission',
        'return_url': return_url,
        'instance': submission,
        'initial': {
            'fund': request.user.fund,
            'author': request.user
        }
    })


@user_passes_test(user_should_be_volunteer)
@require_POST
def remove_submission(request, id):
    submission = get_object_or_404(
        Submission.objects.filter(fund=request.user.fund), pk=id)
    return_url = reverse('submissions:get_list')

    if not submission_can_be_edited(submission, request.user):
        raise ApplicationError(
            'Submission cannot be removed. It is in progress', return_url)

    submission.delete()

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_POST
def send_submission(request, id):
    submission = get_object_or_404(
        Submission.objects.filter(fund=request.user.fund), pk=id)

    submission.save()
    
    from django.conf import settings
    send_submssions.apply_async(args=[submission.id], queue=settings.DEFAULT_QUEUE_NAME)

    return redirect(reverse('submissions:get_submission_details', args=[id]))


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_submission_ward(request, id):
    submission = get_object_or_404(
        Submission.objects.filter(fund=request.user.fund), pk=id)

    if not submission_can_be_edited(submission, request.user):
        raise ApplicationError(
            'Ward cannot be added to submission.',
            reverse('submissions:get_submission_details', args=[id]))

    if request.method == 'POST':
        form = AttachWardToTargetForm(request.POST, initial={
            'target': submission})
        if form.is_valid():
            form.save()

    request.method = 'GET'
    return render(request, 'add_submission_ward.html', {
        'model_name': 'submission',
        'submission': submission
    })


@user_passes_test(user_should_be_volunteer)
@require_POST
def remove_submission_ward(request, id, ward_id):
    submission = get_object_or_404(
        Submission.objects.filter(fund=request.user.fund), pk=id)
    ward = get_object_or_404(submission.wards, pk=ward_id)
    submission.wards.remove(ward)

    return redirect(reverse('submissions:get_submission_details', args=[id]))
