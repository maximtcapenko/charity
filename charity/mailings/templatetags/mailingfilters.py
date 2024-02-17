from django import template

from mailings import requirements

register = template.Library()


@register.filter
def mailing_group_is_ready_to_be_removed(group, user):
    return requirements.mailing_group_is_ready_to_be_removed(group)


@register.filter
def template_is_ready_to_be_removed(template, user):
    return requirements.template_is_ready_to_be_removed(template)
