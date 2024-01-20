from django.utils.safestring import mark_safe
from django.template import loader

from commons.functions import should_be_approved


class TaskStateCardRenderer:
    def __init__(self, task, request):
        self.request = request
        self.task = task
        self.state_template_name = 'partials/task_card_state.html'

    def as_card(self):
        return mark_safe(self._render())

    def _render(self):
        process = self.task.process
        process_states = process.states.all()
        task_states_dict = {}

        task_states_list = self.task.states.select_related('approvement').all()
        for state in task_states_list:
            states = task_states_dict.get(state.state_id)
            if not states:
                task_states_dict[state.state_id] = [state]
            else:
                states.append(state)

        current_task_state = TaskStateCardRenderer._resolve_current_task_state(
            self.task, task_states_list)
        html = ''

        """if no current task state then validate budget approvement"""
        if not current_task_state:
            if self.task.expense:
                current_state_is_approved = should_be_approved(self.task.expense)
            else:
                current_state_is_approved = False
        else:
            current_state_is_approved = should_be_approved(current_task_state)
            
        for process_state in process_states:
            task_states_list = task_states_dict.get(process_state.id)

            btn_should_be_disabled = True

            if current_state_is_approved:
                if task_states_list:
                    task_state = task_states_list[-1]
                    btn_should_be_disabled = should_be_approved(task_state)
                else:
                    btn_should_be_disabled = False

            """render card"""
            html += loader.render_to_string(self.state_template_name, {
                'process_state': process_state,
                'task_id': self.task.id,
                'current_state': current_task_state if current_task_state and \
                      task_states_list and current_task_state in task_states_list else None,
                'task_states': task_states_list,
                'css_class': f'card mb-3 {"border-primary" if current_task_state and process_state.id == current_task_state.state_id else ""}',
                'btn_class': f'btn btn-primary {"disabled" if btn_should_be_disabled else ""}'

            }, self.request, using=None)

        return html

    @staticmethod
    def _resolve_current_task_state(task, states):
        for state in states:
            if state.id == task.state_id:
                return state

        return None
