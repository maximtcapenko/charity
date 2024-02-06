from django.db.models import Exists, Q, Model, OuterRef


def project_is_ready_to_be_completed(project):
    all_tasks_count = project.tasks.count()
    done_tasks_count = project.tasks.filter(is_done=True).count()
    return all_tasks_count == done_tasks_count


def user_should_be_project_author_or_leader(user, project):
    return user.id in [project.leader.id, project.author.id]


def project_should_not_contain_any_tasks(project):
    if issubclass(project.__class__, Model):
        return not project.tasks.exists()
    else:
        return project.tasks_count == 0


def process_should_not_be_used_by_any_tasks(process, project):
    if issubclass(process.__class__, Model):
        return not process.tasks.filter(project=project).exists()
    else:
        return process.project_tasks_count == 0


def ward_should_not_be_used_by_any_tasks(ward, project):
    if issubclass(ward.__class__, Model):
        return not project.wards.filter(
            Q(id=ward.id) &
            Exists(project.tasks.filter(ward=OuterRef('pk')))).exists()
    else:
        return ward.project_tasks_count == 0


def reviewer_should_not_be_used_by_any_tasks(reviewer, project):
    if issubclass(reviewer.__class__, Model):
        return not project.tasks.filter(
            Q(states__approvement__author__id=reviewer.id) |
            Q(state__approvement__author__id=reviewer.id) |
            Q(reviewer__id=reviewer.id)).exists()
    else:
        if reviewer.id == project.leader.id:
            return False
        return not reviewer.project_tasks_exists
