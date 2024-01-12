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
def notifications_list(notifications):
    result = ''
    groups = itertools.groupby(notifications, lambda x: x.title)

    for key, group in groups:
        result += f'<li><a class="dropdown-item" href="#">{key}</a>'
        result += f'<li><hr class="dropdown-divider" /></li>'
        for index, notification in enumerate(group):
            url = reverse('view_notification_details', args=[notification.id])
            if index == 0:
                result += f'<li><a class="dropdown-item" href="{url}">{notification.short} <span class="badge rounded-pill bg-danger">new</span></a></li>'
            else:
                result += f'<li><a class="dropdown-item" href="{url}">{notification.short}</a></li>'

    if result == '':
        result += '<li><a class="dropdown-item" href="#">No new notifications</a></li>'

    return mark_safe(result)