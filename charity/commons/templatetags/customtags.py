import itertools

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from .nodes import ViewNode

register = template.Library()


@register.filter
def phone_number(number):
    if not number or len(number) != 12:
        return number
    '''TODO: make it more cleverer'''
    country_code = number[0:3]
    network_code = number[3:5]
    second = number[5:8]
    third = number[8:]

    return f'+({country_code}) {network_code} {second}-{third}'


@register.filter(is_safe=True)
def cover(item, arg=33):
    if item.cover:
        result = f'<img src="{ item.cover.url }"  height={arg} width={arg}  class="rounded-circle"/>'
    else:
        result = f'<img src="..."  height={arg} width={arg}  class="rounded-circle"/>'
    return mark_safe(result)


@register.filter(is_safe=True)
def thumbnail(item, arg=30):
    if item.cover:
        result = f'<img src="{ item.cover.url }"  height={arg} width={arg}  class="rounded"/>'
    else:
        result = f'<img src="..."  height={arg} width={arg}  class="rounded"/>'
    return mark_safe(result)


@register.filter
def dict_value(dictionary, key):
    return dictionary.get(key)


@register.filter(is_safe=True)
def notifications_list(notifications_queryset):
    result = ''
    groups = itertools.groupby(notifications_queryset, lambda x: x.title)

    for key, group in groups:
        result += f'<li><a class="dropdown-item" href="#"><strong>{key}</strong></a>'
        result += f'<li><hr class="dropdown-divider"/></li>'
        for index, notification in enumerate(group):
            url = reverse('view_notification_details', args=[notification.id])
            if index == 0:
                result += f'<li><a class="dropdown-item" href="{url}">{notification.short} <span class="badge rounded-pill bg-danger">new</span></a></li>'
            else:
                result += f'<li><a class="dropdown-item" href="{url}">{notification.short}</a></li>'

    if result == '':
        result += '<li><a class="dropdown-item" href="#">No new notifications</a></li>'

    return mark_safe(result)


@register.filter(is_safe=True)
def active_tasks_list(tasks_queryset):
    result = ''
    tasks = tasks_queryset.values('id', 'name', 'project__name')
    groups = itertools.groupby(tasks, lambda x: x['project__name'])
    for key, group in groups:
        result += f'<li><a class="dropdown-item" href="#"><strong>{key}</strong></a>'
        result += f'<li><hr class="dropdown-divider"/></li>'
        for index, task in enumerate(group):
            url = reverse('tasks:get_details', args=[task['id']])
            if index == 0:
                result += f'<li><a class="dropdown-item" href="{url}">{task["name"]} <span class="badge rounded-pill bg-danger">new</span></a></li>'
            else:
                result += f'<li><a class="dropdown-item" href="{url}">{task["name"]}</a></li>'

    if result == '':
        result += '<li><a class="dropdown-item" href="#">No assigned tasks</a></li>'

    return mark_safe(result)


@register.tag
def render_partial(parser, token):
    """
    Inserts the output of a view, using fully qualified view name,
    or view name from urls.py.

      {% render_partial view_name arg[ arg2] k=v [k2=v2...] %}

    IMPORTANT: the calling template must receive a context variable called
    'request' containing the original HttpRequest. This means you should be OK
    with permissions and other session state.

    (Note that every argument will be evaluated against context except for the
    names of any keyword arguments.)
    """
    args = []
    kwargs = {}
    tokens = token.split_contents()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError(
            '%r tag requires one or more arguments' %
            token.contents.split()[0]
        )
    tokens.pop(0)  # tag name
    view_name = tokens.pop(0)
    for token in tokens:
        equals = token.find('=')
        if equals == -1:
            args.append(token)
        else:
            kwargs[str(token[:equals])] = token[equals+1:]
    return ViewNode(view_name, args, kwargs)


@register.simple_tag(takes_context=True)
def get_context_values(context, *keys):
    result = {}
    for key in keys:
        result[key] = context.get(key, None)
    return result
