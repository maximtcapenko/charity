from django import template

from projects import requirements
from projects.models import Project

register = template.Library()


@register.filter
def validate_pre_requirements(project, user):
    return requirements.user_should_be_project_author_or_leader(user, project)


@register.filter
def project_should_not_contain_any_tasks(project):
    return requirements.project_should_not_contain_any_tasks(project)
