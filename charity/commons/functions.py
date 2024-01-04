from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from .exceptions import NullArgumentError


def user_should_be_volunteer(user):
    return hasattr(user, 'volunteer_profile') and user.volunteer_profile is not None


def user_should_be_superuser(user):
    return user.is_superuser


def render_generic_form(request, form_class, context):
    params = {}

    post_form_initial = context.get('post_form_initial')
    get_form_initial = context.get('get_form_initial')
    instance = context.get('instance')

    if instance:
        params['instance'] = instance

    if request.method == 'POST':
        if post_form_initial:
            params['initial'] = post_form_initial

        form = form_class(
            request.POST, **params)

        if form.is_valid():
            form.save()
            return redirect(context['return_url'])
        else:
            return render(request, 'generic_createform.html', {
                'return_url': context['return_url'],
                'title': context['title'],
                'form': form
            })
    elif request.method == 'GET':
        if get_form_initial:
            params['initial'] = get_form_initial

        return render(request, 'generic_createform.html', {
            'return_url': context['return_url'],
            'title': context['title'],
            'form': form_class(**params)
        })
    else:
        return HttpResponseNotAllowed([request.method])


def get_argument_or_error(argument, arguments):
    argument = arguments.get(argument)
    if not argument:
        raise NullArgumentError('Argument %s is none' % argument)
    return argument
