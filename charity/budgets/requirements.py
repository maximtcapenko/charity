def user_should_be_budget_owner(user, instnce):
    return user.id in [instnce.manager.id, instnce.author.id]


def user_should_be_budget_item_editor(user, instance):
    return user.id in [instance.reviewer.id, instance.author.id] or user_should_be_budget_owner(user, instance.budget)


def user_should_be_budget_item_reviewer(user, instance):
    return user.id in [instance.reviewer.id,  instance.budget.manager.id]
