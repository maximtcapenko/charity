
def task_state_is_ready_for_review_request(state, user, task):
    if not user or not task:
        return False

    if user == task.assignee:
        if not state.approvement and not state.request_review:
            return True
        elif not state.request_review and state.approvement and state.approvement.is_rejected:
            return True
    else:
        return False


def task_state_is_ready_for_review(state, user, task):
    if not user or not task:
        return False
   
    if state.request_review and user == state.request_review.reviewer:
        if not state.approvement or state.approvement.is_rejected:
            return True
    else:
        return False