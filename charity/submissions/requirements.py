def submission_can_be_edited(submission, user):
    return submission.author == user
