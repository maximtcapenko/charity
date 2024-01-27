class Warnings:
    ASSIGNEE_CANNOT_BE_A_TASK_REVIEWER = 'The assignee cannot be a task reviewer.'
    REVIEWER_IS_NOT_PROJECT_REVIEWER = 'The current task reviewer is not a project reviewer.'
    END_DATE_CANNOT_BE_LESS_THAN_START_DATE = 'The end date cannot be less than the start date.'
    REVIEWER_CANNOT_BE_A_TASK_ASSIGNEE = 'The reviewer cannot be assigned to perform the task.'
    TASK_STATE_IS_NOT_READY_FOR_REVIEW = 'The current status of the task is not ready for review. Check the prerequisites.'
    TASK_STATE_IS_APPROVED = 'The current task status has already been approved and cannot be revised again.'
    TASK_STATE_REVIEW_REQUEST_HAS_BEEN_SENT = 'Review request has already been sent.'
    TASK_IS_NOT_INCLUDED_IN_BUDGET = 'The current task has an estimate, but is not included in any budget.'
    TASK_IN_A_BUDGET_BUT_BUDGET_IS_NOT_APPROVED = 'The current task has an estimate, but the budget has not yet been approved.'
    TASK_IN_A_BUDGET_BUT_BUDGET_IS_REJECTED = 'The current task has an estimate, but the budget has been rejected.'
    TASK_EXPENSE_IS_REJECTED = 'The current task has an estimate, but estimation has been rejected.'
    CURRENT_TASK_IS_NOT_APPROVED = 'The current task status is not approved.'
    CURRENT_USER_IS_NOT_TASK_REVIEWER = 'The current user is not an task reviewer.'
    CURRENT_USER_IS_NOT_TASK_ASSIGNEE = 'The current user is not an task assignee.'