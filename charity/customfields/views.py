from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from commons import DEFAULT_PAGE_SIZE
from commons.functions import render_generic_form, user_should_be_volunteer
from wards.models import Ward

from .forms import CustomFieldCreateForm
from .models import CustomField


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_custom_field(request):
    fund = request.user.volunteer_profile.fund
    content_type = ContentType.objects.get_for_model(Ward)
    return render_generic_form(
        request=request, form_class=CustomFieldCreateForm,
        context={
            'return_url': reverse("customfields:get_fields_configuration"),
            'title': 'Add custom field',
            'initial': {
                'fund': fund,
                'content_type': content_type
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_custom_field(request, id):
    fund = request.user.volunteer_profile.fund
    custom_field = get_object_or_404(
        CustomField.objects.filter(fund=fund), pk=id)
    content_type = ContentType.objects.get_for_model(Ward)
    return render_generic_form(
        request=request, form_class=CustomFieldCreateForm,
        context={
            'return_url': reverse("customfields:get_fields_configuration"),
            'title': 'Add custom field',
            'initial': {
                'fund': fund,
                'content_type': content_type
            },
            'instance': custom_field
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_fields_configuration(request):
    fund = request.user.volunteer_profile.fund
    paginator = Paginator(CustomField.objects.filter(
        fund=fund), DEFAULT_PAGE_SIZE)

    return render(request, 'fields_configuration.html', {
        'fund': fund,
        'page': paginator.get_page(request.GET.get('page'))
    })
