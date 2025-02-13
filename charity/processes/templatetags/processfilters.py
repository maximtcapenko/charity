from django import template

from processes import requirements

register = template.Library()

@register.filter
def new_step_can_be_added_to_process(process):
    return requirements.new_step_can_be_added_to_process(process)

