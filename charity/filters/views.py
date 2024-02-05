import json
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from commons import DEFAULT_PAGE_SIZE
from commons.functional import render_generic_form, user_should_be_volunteer

from customfields.models import CustomField

from .forms import AddExpressionValueForm, CreateFilterForm, \
    CreateFilterExpressionForm
from .models import Filter, Expression
from .widgets import ExpressionValueWidget


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_filter(request, model_name):
    fund = request.user.fund
    return_url = reverse('filters:get_list', args=[model_name])
    content_type = get_object_or_404(ContentType, model=model_name)
    return render_generic_form(
        request,
        form_class=CreateFilterForm,
        context={
            'title': 'Add new filter',
            'return_url': return_url,
            'initial': {
                'author': request.user,
                'fund': fund,
                'content_type': content_type
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_filter_details(request, id):
    return render(request, 'filter_details.html', {
        'filter': get_object_or_404(
            Filter.objects.prefetch_related(
                Prefetch(
                    'expressions',
                    Expression.objects.select_related('field', 'field__attribute')))
            .filter(fund=request.user.fund), pk=id)})


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def edit_filter_details(request, id):
    fund = request.user.fund
    filter = get_object_or_404(Filter.objects.filter(fund=fund), pk=id)
    return_url = reverse('filters:get_details', args=[id])

    return render_generic_form(
        request,
        form_class=CreateFilterForm,
        context={
            'title': 'Edit filter',
            'return_url': return_url,
            'instance': filter,
            'initial': {
                'author': request.user,
                'fund': fund,
                'content_type': filter.content_type
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['POST'])
def remove_filter(request, id):
    fund = request.user.fund
    filter = get_object_or_404(Filter.objects.filter(fund=fund), pk=id)
    return_url = reverse('filters:get_list', args=[filter.content_type.model])
    filter.delete()

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_expression(request, id):
    fund = request.user.fund
    return_url = reverse('filters:get_details', args=[id])
    return render_generic_form(
        request,
        form_class=CreateFilterExpressionForm, context={
            'return_url': return_url,
            'title': 'Add new filter expression',
            'initial': {
                'author': request.user,
                'fund': fund,
                'filter': get_object_or_404(Filter.objects.filter(fund=fund), pk=id)
            }
        })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_expression_details(request, id, expression_id):
    fund = request.user.fund
    expression = get_object_or_404(
        Expression.objects.select_related('field')
        .filter(filter__id=id, filter__fund=fund), pk=expression_id)

    return render(request, 'filter_expression_details.html', {
        'expression': expression
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def add_expression_value(request, id, expression_id):
    fund = request.user.fund
    return_url = reverse('filters:get_expression_details',
                         args=[id, expression_id])
    expression = get_object_or_404(Expression.objects.filter(
        filter_id=id, filter__fund=fund), pk=expression_id)
    return render_generic_form(request, form_class=AddExpressionValueForm, context={
        'title': 'Add expression value',
        'return_url': return_url,
        'initial': {
            'expression': expression
        }
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET', 'POST'])
def remove_expression(request, id, expression_id):
    fund = request.user.fund
    return_url = reverse('filters:filter_details', args=[id])
    expression = get_object_or_404(Expression.objects.filter(
        filter_id=id, filter__fund=fund), pk=expression_id)
    expression.delete()

    return redirect(return_url)


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_list(request, model_name):
    fund = request.user.fund
    content_type = get_object_or_404(ContentType, model=model_name)

    paginator = Paginator(Filter.objects.filter(
        fund=fund, content_type=content_type), DEFAULT_PAGE_SIZE)

    return render(request, 'filter_list.html', {
        'fund': fund,
        'content_type': content_type,
        'page': paginator.get_page(request.GET.get('page'))
    })


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_filed_value_input_details(request):
    field_id = request.GET.get('field_id')
    field = get_object_or_404(CustomField, pk=field_id)
    return HttpResponse(json.dumps(ExpressionValueWidget.get_rendered_value_widget(request, field)))


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_select_filters(request, model_name):
    selected_filter = request.GET.get('filter_id')
    filters = Filter.objects.filter(
        fund=request.user.fund,
        content_type__model=model_name).all()

    return render(request, 'partials/select_filter.html', {
        'filters': filters,
        'selected_filter': selected_filter
    })
