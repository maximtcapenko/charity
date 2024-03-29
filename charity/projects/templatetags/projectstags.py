from django.utils.safestring import mark_safe
from django import template
from django.template import loader

from commons.functional import wrap_dict_set_to_objects_list
from tasks.querysets import get_project_tasks_comments_count_queryset, \
    get_project_tasks_states_count_queryset

register = template.Library()


@register.inclusion_tag("partials/project_tasks_card.html", takes_context=True)
def render_tasks_board(context, project, tasks):
    request = context["request"]
    task_template_name = 'partials/project_task_card.html'
    items_count = context.get('items_count')

    def _get_context():
        todo_tasks = ''
        in_progress_tasks = ''
        on_review_tasks = ''
        done_tasks = ''

        comments = wrap_dict_set_to_objects_list(
            get_project_tasks_comments_count_queryset(project))

        progresses = wrap_dict_set_to_objects_list(
            get_project_tasks_states_count_queryset(project))

        for task in tasks:
            comments_count = next(
                filter(lambda x: x.id == task.id, comments))
            progress = next(
                filter(lambda x: x.id == task.id, progresses))

            if not task.is_started and not task.is_done:
                todo_tasks += loader.render_to_string(task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count,
                    'progress': progress
                }, request, using=None)

            elif task.is_started and not task.is_on_review and not task.is_done:
                in_progress_tasks += loader.render_to_string(task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count,
                    'progress': progress
                }, request, using=None)
            elif task.is_on_review:
                on_review_tasks += loader.render_to_string(task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count,
                    'progress': progress
                }, request, using=None)

            elif task.is_done:
                done_tasks += loader.render_to_string(task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count,
                    'progress': progress
                }, request, using=None)

        return {
            'todo_tasks': mark_safe(todo_tasks),
            'in_progress_tasks': mark_safe(in_progress_tasks),
            'on_review_tasks': mark_safe(on_review_tasks),
            'done_tasts': mark_safe(done_tasks),
            'items_count': items_count,
            'page': tasks
        }

    return _get_context()


@register.inclusion_tag('partials/project_progress.html', takes_context=True)
def render_project_progress(context, project):
    complete_in_percents = 0

    if project.tasks_count > 0:
        complete_in_percents = round(
            project.done_tasks_count / project.tasks_count * 100)

    return {
        'project': project,
        'complete_in_percents': complete_in_percents
    }
