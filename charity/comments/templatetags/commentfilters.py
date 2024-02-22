from django import template

from comments import requirements


register = template.Library()


@register.filter
def comment_is_ready_to_be_added(context):
    content_type = context.get('content_type')
    target = context.get('target')
    return requirements.comment_is_ready_to_be_added(target, content_type)
