
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


def task_is_ready_to_be_completed(task, user):
    process_state_ids = list(task.process.states.values_list('id', flat=True))
    completed_states_ids = list(task.states.filter(
        approvement__is_rejected=False).values_list('state_id', flat=True))

    return process_state_ids == completed_states_ids and not task.is_done


def task_file_is_ready_to_be_removed(task, file):
    return not task.is_done


def task_file_is_ready_to_be_added(task):
    return not task.is_done


def task_comment_is_ready_to_be_added(task):
    return not task.is_done
