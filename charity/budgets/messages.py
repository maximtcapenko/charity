class Warnings:
    CURRENT_USER_IS_NOT_PERMITTED = 'The current user cannot perform operation because they are not the author or manager of the budget.'
    INCOME_CANNOT_BE_DELETED_BUDGET_APPROVED = 'Income cannot be deleted because the budget has been approved'
    INCOME_CANNOT_BE_DELETED_IT_HAS_BEEN_APPROVED = 'Income cannot be deleted because it has approvement'
    EXPENSE_CANNOT_BE_DELETED_BUDGET_APPROVED = 'Expense cannot be deleted because the budget has been approved'
    EXPENSE_CANNOT_BE_DELETED_IT_HAS_BEEN_APPROVED = 'Expense cannot be deleted because it has approvement'
    BUDGET_CANNOT_BE_DELETED_IT_HAS_INCOMES = 'The budget cannot be removed because it has incomes or expenses.'
    BUDGET_REVIEWER_MUST_EXISTS = 'The budget must have at least one reviewer.'
    BUDGET_REVIEWER_IS_A_MANAGER = 'The reviewer cannot be removed from the budget because the reviewer is a manager.'
    BUDGET_REVIEWER_CANNOT_BE_REMOVED_REVIEWS_EXISTS = 'A reviewer cannot be removed from the budget because of budget approved reviews.'
    BUDGET_REVIEWER_CANNOT_BE_REMOVED_INCOMES_REVIEWS_EXISTS = 'A reviewer cannot be removed from a budget because of reviewed incomes in the budget.'
    BUDGET_REVIEWER_CANNOT_BE_REMOVED_EXPENSES_REVIEWS_EXISTS = 'A reviewer cannot be removed from a budget because of reviewed expenses in the budget.'
    BUDGET_REVIEWER_NOT_ASSIGNED = 'Reviewer not assigned.'
    BUDGET_CANNOT_BE_CHANGED_IT_HAS_BEEN_APPROVED = 'The budget has been approved and cannot be changed.'
    BUDGET_CANNOT_BE_CHANGED_IT_HAS_BEEN_CLOSED = 'The budget has been closed and cannot be changed.'
    BUDGET_CANNOT_BE_APPROVED_NO_BUDGET_ITEMS = 'The budget cannot be approved, there are no income and expenses.'
    BUDGET_CANNOT_BE_APPROVED_NO_APPROVED_BUDGET_ITEMS = 'The budget cannot be approved, there are not approved income and expenses.'
    BUDGET_MANAGER_CANNOT_BE_UNDEFINED = 'A budget manager has already been assigned. This field cannot be null or empty.'
    BUDGET_ITEM_HAS_BEEN_ALREADY_APPROVED = 'The budget item has been already approved.'
    BUDGET_ITEM_CANNOT_BE_CHANGED_IT_HAS_BEEN_APPROVED = 'The budget item has been approved and cannot be changed.'
    CURRENT_USER_IS_NOT_BUDGET_ITEM_REVIEWER = 'The current user is not budget item reviewer and cannot review it.'
    CURRENT_USER_IS_NOT_BUDGET_REVIEWER = 'The current user is not budget reviewer and cannot review budget.'
    INCOME_CANNOT_BE_ADDED_BUDGET_HAS_BEEN_APPROVED = 'New income cannot be added because the current budget has been approved.'
    NO_CONTIBUTION = 'No contribution available'
    INCOME_SHOULD_BE_POSITIVE = 'Income cannot be empty or negative'
    EXPENSE_SHOULD_BE_POSITIVE = 'Expense cannot be empty or negative'
    EXPENSE_CANNOT_BE_ADDED_BUDGET_HAS_BEEN_APPROVED = 'New expense cannot be added because the current budget has been approved.'