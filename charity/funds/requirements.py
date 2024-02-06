def contribution_is_ready_to_be_removed(contribution, user):
    if contribution.contributor.is_internal:
        return True
    if contribution.incomes_exist:
        return False
