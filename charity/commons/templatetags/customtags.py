from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def cover(item):
    result = f'<img src="{ item.cover.url }"  height=35 width=35  class="rounded-circle"/>'
    return mark_safe(result)