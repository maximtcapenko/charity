from django.utils.safestring import mark_safe
from django import template
from django.template import loader

from commons.functional import should_be_approved, wrap_dict_set_to_objects_list
from tasks.querysets import get_task_state_review_count_queryset

register = template.Library()


@register.inclusion_tag('partials/task_states_list.html', takes_context=True)
def render_task_states_board(context, task):
    state_template_name = 'partials/task_item_state.html'

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

    for state in task_states_list:
        task_states_dict.setdefault(state.state_id, []).append(state)

    current_task_state = _resolve_current_task_state(
        task, task_states_list)
    
    html = ''

    """Validate budget approvement"""
    is_task_budget_approved = should_be_approved(task.expense) and should_be_approved(task.expense.budget) \
        if task.expense else False
    
    prev_task_states_list = None
    for process_state in process_states:
        btn_should_be_disabled = True

        if len(task_states_dict) == 0:
            if is_task_budget_approved:
                btn_should_be_disabled = False
        else:
            task_states_list = task_states_dict.get(process_state.id)
            if prev_task_states_list and not task_states_list:
                 task_state = prev_task_states_list[0]
                 btn_should_be_disabled = not should_be_approved(task_state)        

            prev_task_states_list = task_states_list

        """render card"""
        html += loader.render_to_string(state_template_name, {
            'process_state': process_state,
            'process_state_state': next(filter(lambda state: state.state_id == process_state.id, task_states_list)) if task_states_list else None,
            'task': task,
            'current_state': current_task_state if current_task_state and
            task_states_list and current_task_state in task_states_list else None,
            'task_states': task_states_list,
            'in_progess': True if current_task_state and process_state.id == current_task_state.state_id else False,
            'btn_css_class': f'{"disabled" if btn_should_be_disabled else ""}'

        }, request, using=None)

    return {'html': mark_safe(html)}


@register.inclusion_tag('partials/task_progress.html', takes_context=True)
def render_task_progress(context, task):
    from processes.models import ProcessState

    states_count = ProcessState.objects.filter(
        process_id=task.process_id).count()
    task_states_count = task.states.filter(
        approvement__is_rejected=False).count()

    complete_in_percents = 0

    if states_count > 0:
        complete_in_percents = round(task_states_count / states_count * 100)

    return {
        'task': task,
        'complete_in_percents': complete_in_percents
    }
