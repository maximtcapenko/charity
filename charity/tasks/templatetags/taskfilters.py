from django import template

from tasks import requirements

register = template.Library()


@register.filter
def task_state_is_ready_for_review_request(state, context):
    user = context.get('user')
    task = context.get('task')

    return requirements.task_state_is_ready_for_review_request(state, user, task)


@register.filter
def task_state_is_ready_for_review(state, context):
    user = context.get('user')
    task = context.get('task')

    return requirements.task_state_is_ready_for_review(state, user, task)
