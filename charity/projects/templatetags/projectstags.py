from django.utils.safestring import mark_safe
from django import template
from django.template import loader

from commons.functions import wrap_dict_set_to_objects_list
from tasks.querysets import get_project_tasks_comments_count_queryset

register = template.Library()


@register.inclusion_tag("partials/project_tasks_card.html", takes_context=True)
def render_tasks_board(context, project, tasks):
    request = context["request"]
    task_template_name = 'partials/project_task_card.html'

    def _get_context():
        todo_tasks = ''
        in_progress_tasks = ''
        on_review_tasks = ''
        done_tasts = ''

        comments = wrap_dict_set_to_objects_list(
            get_project_tasks_comments_count_queryset(project))

        for task in tasks:
            comments_count = next(
                filter(lambda x: x.id == task.id, comments), None)
            if not task.is_started:
                todo_tasks += loader.render_to_string(task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count if comments_count else 0
                }, request, using=None)

            elif task.is_started and not task.is_on_review:
                in_progress_tasks += loader.render_to_string(task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count if comments_count else 0
                }, request, using=None)
            elif task.is_on_review:
                on_review_tasks += loader.render_to_string(task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count if comments_count else 0
                }, request, using=None)

            elif task.is_done:
                done_tasts += loader.render_to_string(task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count if comments_count else 0
                }, request, using=None)

        return {
            'todo_tasks': mark_safe(todo_tasks),
            'in_progress_tasks': mark_safe(in_progress_tasks),
            'on_review_tasks': mark_safe(on_review_tasks),
            'done_tasts': mark_safe(done_tasts),
            'page': tasks
        }

    return _get_context()
