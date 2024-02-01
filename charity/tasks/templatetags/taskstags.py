from django.utils.safestring import mark_safe
from django import template
from django.template import loader

from commons.functions import should_be_approved, wrap_dict_set_to_objects_list
from tasks.querysets import get_task_state_review_count_queryset

register = template.Library()


@register.inclusion_tag('partials/task_states_list.html', takes_context=True)
def render_task_states_board(context, task):
    state_template_name = 'partials/task_card_state.html'

    def get_state_reviews_count(state_id, reviews):
        result = next(
            filter(lambda x: x.id == state_id, reviews), None)
        return result.reviews_count if result else 0

    def _resolve_current_task_state(task, states):
        for state in states:
            if state.id == task.state_id:
                return state

        return None

    request = context['request']
    process = task.process
    process_states = process.states.all()
    task_states_dict = {}

    task_states_list = task.states.select_related(
        'approvement', 'request_review').all()

    reviews = wrap_dict_set_to_objects_list(
        get_task_state_review_count_queryset(task))

    for state in task_states_list:
        states = task_states_dict.get(state.state_id)
        if not states:
            task_states_dict[state.state_id] = [state]
        else:
            states.append(state)

    current_task_state = _resolve_current_task_state(
        task, task_states_list)
    html = ''

    """if no current task state then validate budget approvement"""
    if not current_task_state:
        if task.expense:
            current_state_is_approved = should_be_approved(
                task.expense)
        else:
            current_state_is_approved = False
    else:
        current_state_is_approved = should_be_approved(current_task_state)

    for process_state in process_states:
        task_states_list = task_states_dict.get(process_state.id)
        reviews_count = 0
        if task_states_list:
            reviews_count = sum(get_state_reviews_count(
                item.id, reviews) for item in task_states_list)

        btn_should_be_disabled = True

        if current_state_is_approved:
            if task_states_list:
                task_state = task_states_list[-1]
                btn_should_be_disabled = should_be_approved(task_state)
            else:
                btn_should_be_disabled = False

        """render card"""
        html += loader.render_to_string(state_template_name, {
            'process_state': process_state,
            'task': task,
            'reviews_count': reviews_count,
            'current_state': current_task_state if current_task_state and
            task_states_list and current_task_state in task_states_list else None,
            'task_states': task_states_list,
            'card_css_class': f'{"border-primary" if current_task_state and process_state.id == current_task_state.state_id else ""}',
            'btn_css_class': f'{"disabled" if btn_should_be_disabled else ""}'

        }, request, using=None)

    return {'html' : mark_safe(html)}


@register.inclusion_tag('partials/task_progress.html', takes_context=True)
def render_task_progress(context, task):
    from processes.models import ProcessState

    states_count = ProcessState.objects.filter(process_id=task.process_id).count()
    task_states_count = task.states.filter(approvement__is_rejected=False).count()

    complete_in_percents = round(task_states_count / states_count * 100) 
  
    return {
        'task': task,
        'complete_in_percents': complete_in_percents
    }