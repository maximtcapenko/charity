import itertools

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def cover(item):
    if item.cover:
        result = f'<img src="{ item.cover.url }"  height=33 width=33  class="rounded-circle"/>'
    else:
        result = f'<img src="..."  height=33 width=33  class="rounded-circle"/>'
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