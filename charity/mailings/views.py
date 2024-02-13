import json

from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from django.views.decorators.http import require_http_methods, require_GET
from commons import DEFAULT_PAGE_SIZE
from commons.functional import render_generic_form, user_should_be_volunteer

from .forms import AddMailingGroupForm, AddMailingRecipientForm, AddMailingTemplateForm
from .models import MailingGroup, MailingTemplate
from .widgets import TemplateFieldsWidget


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_group(request):
    return render_generic_form(
        request=request, form_class=AddMailingGroupForm,
        context={
            'title': 'Add group',
            'return_url': f'{reverse("mailings:get_gorups_list")}',
            'initial': {
                'fund': request.user.fund,
                'author': request.user
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_gorups_list(request):
    paginator = Paginator(
        MailingGroup.objects.filter(fund=request.user.fund), DEFAULT_PAGE_SIZE)

    return render(request, 'goups_list.html', {
        'page': paginator.get_page(request.GET.get('page')),
        'items_count': paginator.count
    })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_group_details(request, id):
    group = get_object_or_404(
        MailingGroup.objects.filter(fund=request.user.fund), pk=id)
    paginator = Paginator(group.recipients.all(), DEFAULT_PAGE_SIZE)
    return render(request, 'group_details.html', {
        'group': group,
        'page': paginator.get_page(request.GET.get('page')),
        'items_count': paginator.count
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_group(request, id):
    group = get_object_or_404(
        MailingGroup.objects.filter(fund=request.user.fund), pk=id)
    return render_generic_form(
        request=request, form_class=AddMailingGroupForm,
        context={
            'title': 'Edit group',
            'return_url': f'{reverse("mailings:get_group_details", args=[id])}',
            'instance': group,
            'initial': {
                'fund': request.user.fund,
                'author': request.user
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_recipient(request, id):
    group = get_object_or_404(
        MailingGroup.objects.filter(fund=request.user.fund), pk=id)
    return render_generic_form(
        request=request, form_class=AddMailingRecipientForm,
        context={
            'title': 'Add recipient',
            'return_url': f'{reverse("mailings:get_group_details", args=[id])}',
            'initial': {
                'group': group,
                'fund': request.user.fund,
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_templates_list(request):
    paginator = Paginator(MailingTemplate.objects.filter(
        fund=request.user.fund).all(), DEFAULT_PAGE_SIZE)
    return render(request, 'templates_list.html', {
        'items_count': paginator.count,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_template(request):
    return render_generic_form(
        request=request, form_class=AddMailingTemplateForm,
        context={
            'title': 'Add template',
            'form_template': 'add_template.html',
            'return_url': f'{reverse("mailings:get_templates_list")}',
            'initial': {
                'author': request.user,
                'fund': request.user.fund,
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_template(request, id):
    template = get_object_or_404(
        MailingTemplate.objects.filter(fund=request.user.fund), pk=id)
    return render_generic_form(
        request=request, form_class=AddMailingTemplateForm,
        context={
            'title': 'Edit template',
            'form_template': 'add_template.html',
            'return_url': f'{reverse("mailings:get_templates_list")}',
            'instance': template,
            'initial': {
                'author': request.user,
                'fund': request.user.fund,
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_content_type_details(request):
    from django.contrib.contenttypes.models import ContentType
    content_type_id = request.GET.get('content_type_id')
    contet_type = get_object_or_404(ContentType, pk=content_type_id)
    widget = TemplateFieldsWidget()
    widget.content_type=contet_type
    widget.template_name='partials/fields.html'

    return HttpResponse(json.dumps({
        'html': widget.render(None, None)
    }))