import importlib

from django import forms
from django.http import HttpResponseNotAllowed
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from . import DEFAULT_PAGE_SIZE
from .exceptions import NullArgumentError
from .mixins import FileUploadMixin
from .models import Base
from .utils import DictObjectWrapper, WrappedPage


def user_should_be_volunteer(user):
    return hasattr(user, 'fund') and user.fund is not None


def user_should_be_superuser(user):
    return user.is_superuser


def render_generic_form(request, form_class, context, read_only=None):
    params = {}
    return_url = context.get('return_url')
    title = context.get('title')

    error_message = 'Required parameter [%s] is not provided'

    if not return_url:
        raise NullArgumentError(error_message % 'return_url')
    if not title:
        raise NullArgumentError(error_message % 'title')

    initial = context.get('initial')
    post_form_initial = context.get('post_form_initial')
    get_form_initial = context.get('get_form_initial')
    instance = context.get('instance')
    form_template = context.get('form_template')

    if instance:
        params['instance'] = instance

    if not form_template:
        if issubclass(form_class, FileUploadMixin):
            form_template = 'generic_multipartform.html'
        else:
            form_template = 'generic_createform.html'

    if request.method == 'POST':
        if initial:
            params['initial'] = initial
        elif post_form_initial:
            params['initial'] = post_form_initial

        if issubclass(form_class, FileUploadMixin):
            form = form_class(
                request.POST, request.FILES, **params)
        else:
            form = form_class(request.POST, **params)

        if form.is_valid() and not read_only:
            form.save()
            return redirect(return_url)
        else:
            return render(request, form_template, {
                'return_url': return_url,
                'title': title,
                'form': form
            })
    elif request.method == 'GET':
        if initial:
            params['initial'] = initial
        elif get_form_initial:
            params['initial'] = get_form_initial

        form = form_class(**params)
        if read_only:
            for field in form.fields:
                form.fields[field].disabled = True

        return render(request, form_template, {
            'return_url': return_url,
            'title': title,
            'form': form,
            'read_only': read_only
        })
    else:
        return HttpResponseNotAllowed([request.method])


def get_argument_or_error(argument, arguments):
    argument = arguments.get(argument)
    if not argument:
        raise ValueError(f'Missing required parameter:{argument}')

    return argument


def validate_modelform_field(field, initial, cleaned_data):
    """
    Check if `field` exists in both dictionaries
    :param `field`: name of field
    :param `initial`: dictionary provided by code user (usual `self.initial property` of Form)
    :param `cleaned_data`: form clead data dictionary (`self.cleaned_data` of Form)
    :raise 'forms.ValidationError'
    """
    target_field = get_argument_or_error(field, initial)
    cleaned_field = cleaned_data[field]
    if target_field.id != cleaned_field.id:
        raise forms.ValidationError(
            f'{field} has different value from initial')


def should_be_approved(target):
    """
    Validates if target object is approved
    """
    return target.approvement and \
        target.approvement.is_rejected == False


def wrap_dict_set_to_objects_list(dicts, model=None):
    return [DictObjectWrapper(dict, model=model) for dict in dicts]


def wrap_dicts_page_to_objects_page(page, model=None):
    """
    Wrapp page with dict items into page with object items
    """
    return WrappedPage(page, model=model)


def get_reviewer_label(user):
    return f'{user.username} ({user.volunteer_profile.title})'


def get_page(queryset, page_number):
    paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)
    page = paginator.get_page(page_number)

    return page, paginator.count


def get_wrapped_page(model, queryset, page_number):
    page, count = get_page(queryset, page_number)

    return wrap_dicts_page_to_objects_page(page, model=model), count


def resolve_rel_attr_path(attr_model, model, path=None, visited=None):
    """
    Resolves an attribute of type `attr_model` from type `model`.
    Returns a full path
    """
    excludes = [User]

    if visited is None:
        visited = set()
    if path is None:
        path = ''

    for field in model._meta.fields:
        if field.is_relation and field.null == False and field.related_model \
                not in excludes and field.related_model not in visited and issubclass(field.related_model, Base):
            path += f'{"" if path == "" else "__"}{field.name}'
            visited.add(field.related_model)
            if field.related_model is attr_model:
                return path
            else:
                return resolve_rel_attr_path(attr_model, field.related_model, path, visited)
    return None


def resolve_many_2_many_attr_path(attr_model, model):
    for field in model._meta.local_many_to_many:
        if field.related_model is attr_model:
            return field.name

    return None


def resolve_many_2_many_attr(attr_model, content_type, id):
    """
    Resolves attribute with type list[`Model`] from `content_type` object
    `content_type`: `ContentType`
    """
    target_attr = resolve_many_2_many_attr_path(
        attr_model, content_type.model_class())
    instance = content_type.model_class().objects.get(pk=id)
    return getattr(instance, target_attr)


def append_to_url_query(request, **kwargs):
    from django.http import QueryDict
    query = QueryDict(request.GET.urlencode(), mutable=True)
    for key in kwargs:
        query[key] = kwargs[key]
    if len(query) > 0:
        return f'?{query.urlencode()}'

    return ''


imports = {}


def get_requirements_module(content_type):
    try:
        key = f'{content_type.app_label}.requirements'
        if not key in imports.keys():
            imports[key] = importlib.import_module(key)
        return imports[key]
    except:
        return None
