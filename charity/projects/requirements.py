from django.db.models import Model


def user_should_be_project_author_or_leader(user, project):
    return user.id in [project.leader.id, project.author.id]


def project_should_not_contain_any_tasks(project):
    if issubclass(project.__class__, Model):
        return not project.tasks.exists()
    else:
        return project.tasks_count == 0
