from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def cover(item):
    result = f'<img src="{ item.cover.url }"  height=33 width=33  class="rounded-circle"/>'
    return mark_safe(result)

@register.filter
def dict_value(dictionary, key):
    return dictionary.get(key)