from django.utils.safestring import mark_safe
from django.template import loader

from commons.functions import wrap_dict_set_to_objects_list
from tasks.querysets import get_project_tasks_comments_count_queryset


class TasksBoardRenderer:
    def __init__(self, project, tasks, request):
        self.request = request
        self.task_template_name = 'partials/project_task_card.html'
        self.tasks_card_template_name = 'partials/project_tasks_card.html'
        self.tasks = tasks
        self.project = project

    def as_card(self):
        todo_tasks = ''
        in_progress_tasks = ''
        on_review_tasks = ''
        done_tasts = ''

        comments = wrap_dict_set_to_objects_list(
            get_project_tasks_comments_count_queryset(self.project))

        for task in self.tasks:
            comments_count = next(
                filter(lambda x: x.id == task.id, comments), None)
            if not task.is_started:
                todo_tasks += '<div class="row mt-2"><div>'+loader.render_to_string(self.task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count if comments_count else 0
                }, self.request, using=None)+'</div></div>'

            elif task.is_started and not task.is_on_review:
                in_progress_tasks += '<div class="row mt-2"><div>'+loader.render_to_string(self.task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count if comments_count else 0
                }, self.request, using=None)+'</div></div>'
            elif task.is_on_review:
                on_review_tasks += '<div class="row mt-2"><div>'+loader.render_to_string(self.task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count if comments_count else 0
                }, self.request, using=None)+'</div></div>'

            elif task.is_done:
                done_tasts += '<div class="row mt-2"><div>'+loader.render_to_string(self.task_template_name, {
                    'task': task,
                    'comments_count': comments_count.comments_count if comments_count else 0
                }, self.request, using=None)+'</div></div>'

        return mark_safe(loader.render_to_string(self.tasks_card_template_name, {
            'todo_tasks': mark_safe(todo_tasks),
            'in_progress_tasks': mark_safe(in_progress_tasks),
            'on_review_tasks': mark_safe(on_review_tasks),
            'done_tasts': mark_safe(done_tasts),
            'page': self.tasks
        }, self.request, using=None))
