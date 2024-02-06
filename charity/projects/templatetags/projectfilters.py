from django import template

from projects import requirements

register = template.Library()


@register.filter
def validate_pre_requirements(project, user):
    return requirements.user_should_be_project_author_or_leader(user, project)


@register.filter
def project_is_ready_to_be_completed(project):
    return requirements.project_is_ready_to_be_completed(project)


@register.filter
def project_should_not_contain_any_tasks(project):
    return requirements.project_should_not_contain_any_tasks(project)


@register.filter
def process_should_bot_be_used_by_any_tasks(process, project):
    return requirements.process_should_not_be_used_by_any_tasks(process, project)


@register.filter
def ward_should_not_be_used_by_any_tasks(ward, project):
    return requirements.ward_should_not_be_used_by_any_tasks(ward, project)


@register.filter
def reviewer_should_not_be_used_by_any_tasks(reviewer, project):
    return requirements.reviewer_should_not_be_used_by_any_tasks(reviewer, project)
