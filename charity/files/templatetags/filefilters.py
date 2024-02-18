from django import template

from files import requirements


register = template.Library()


@register.filter
def file_is_ready_to_be_removed(file, context):
    content_type = context.get('content_type')
    target = context.get('target')
    return requirements.file_is_ready_to_be_removed(file, target, content_type)


@register.filter
def file_is_ready_to_be_added(context):
    content_type = context.get('content_type')
    target = context.get('target')
    return requirements.file_is_ready_to_be_added(target, content_type)
