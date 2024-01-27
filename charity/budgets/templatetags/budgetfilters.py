from django import template

from commons.functions import should_be_approved
from budgets import requirements

register = template.Library()


@register.filter
def budget_is_ready_to_be_removed(budget, user):
    return not budget.incomes_exist and not should_be_approved(budget) and requirements.user_should_be_budget_owner(user, budget)


@register.filter
def budget_item_is_ready_to_be_removed(item, user):
    return not should_be_approved(item) and requirements.user_should_be_budget_owner(user, item.budget)


@register.filter
def budget_reviewer_can_be_added(budget, user):
    return not should_be_approved(budget) and requirements.user_should_be_budget_owner(user, budget)


@register.filter
def budget_item_can_be_added(budget, user):
    return not should_be_approved(budget) and requirements.user_should_be_budget_owner(user, budget)


@register.filter
def budget_can_be_edited(budget, user):
    return not should_be_approved(budget) and requirements.user_should_be_budget_owner(user, budget)


@register.filter
def budget_item_can_be_edited(item, user):
    return not should_be_approved(item) and requirements.user_should_be_budget_item_editor(user, item)


@register.filter
def budget_item_can_be_reviewed(item, user):
    return not should_be_approved(item) and requirements.user_should_be_budget_item_reviewer(user, item)
