class Warnings:
    ASSIGNEE_CANNOT_BE_A_TASK_REVIEWER = 'The assignee cannot be a task reviewer.'
    REVIEWER_IS_NOT_PROJECT_REVIEWER = 'The current task reviewer is not a project reviewer.'
    END_DATE_CANNOT_BE_LESS_THAN_START_DATE = 'The end date cannot be less than the start date.'
    REVIEWER_CANNOT_BE_A_TASK_ASSIGNEE = 'The reviewer cannot be assigned to perform the task.'
    TASK_IS_NOT_READY_TO_BE_COMPLETED = 'Task is nor ready to be completed. It has unapproved states.'
    CONTRIBUTOR_SHOULD_BE_INTERNAL = 'Selected contributor is not internal usage.'
    ACTUAL_EXPENSE_IS_BIGGER_TAHN_APPROVED = 'The actual expense amount is bigger than approved expense amount.'
    TASK_HAS_EXPENSES_ACUTAL_EXPENSE_AMOUNT_SHOULD_BE_INDICATED = 'The task has expenses. The actual amount of expenses should be indicated.'
    CONTRIBUTOR_SHOULD_BE_INDICATED = 'Task has actual expense amount and it less then approved expense amount. The contributor should be indicated for payout contribution.'
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