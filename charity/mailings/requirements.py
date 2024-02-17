def mailing_group_is_ready_to_be_removed(group):
    return not group.submissions.exists()
