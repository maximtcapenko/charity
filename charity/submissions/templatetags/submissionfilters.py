from django import template

from submissions import requirements

register = template.Library()


@register.filter
def submission_can_be_edited(value, user):
    return requirements.submission_can_be_edited(value, user)
