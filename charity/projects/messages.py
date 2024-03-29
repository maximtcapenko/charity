class Warnings:
    PROJET_CANNOT_BE_COMPLETED = 'Project cannot be completed due running tasks.'
    PROJECT_PROCESS_TASKS_EXIST = 'A process cannot be removed from a project because it is used by tasks.'
    PROJECT_TASK_ISRUNNING ='The task cannot be removed from the project because the task is running or has a cost.'
    ASSET_CANNOT_BE_REMOVED_TASKS_EXIST = 'Adoptee cannot be removed from a project due to its use in tasks.'
    PROJECT_REVIEWER_TASKS_EXIST ='A reviewer cannot be removed from a project due to reviewed tasks in the project.'
    PROJECT_REVIEWER_MUST_EXISTS = 'The project must have at least one reviewer.'
    LEADER_CANNOT_BE_REMOVED_FROM_PROJECT_REVIEWERS = 'A project leader cannot be removed from reviewers list.'
    EMPTY_PROCESS_CANNOT_BE_ADDED = 'Empty process cannot be added to the project.'
    PROJECT_LEADER_CANNOT_BE_UNDEFINED = 'A project leader has already been assigned. This field cannot be null or empty.'
    PROJECT_TASKS_EXIST = 'The project cannot be removed because it has tasks.'
    CURRENT_USER_IS_NOT_PERMITTED = 'The current user cannot perform operation because they are not the author or manager of the project.'
