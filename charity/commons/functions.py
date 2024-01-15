from django import forms
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from .exceptions import NullArgumentError, ApplicationError
from .mixins import FileUploadMixin


def user_should_be_volunteer(user):
    return hasattr(user, 'volunteer_profile') and user.volunteer_profile is not None


def user_should_be_superuser(user):
    return user.is_superuser


def render_generic_form(request, form_class, context):
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

    if instance:
        params['instance'] = instance

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

        if form.is_valid():
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

        return render(request, form_template, {
            'return_url': return_url,
            'title': title,
            'form': form_class(**params)
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
    return target.approvement_id and \
        target.approvement.is_rejected == False
