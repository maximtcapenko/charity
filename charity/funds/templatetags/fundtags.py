from django import template

from funds import requirements

register = template.Library()


@register.filter
def contribution_is_ready_to_be_removed(contribution, user):
    return requirements.contribution_is_ready_to_be_removed(contribution, user)
