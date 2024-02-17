def submission_can_be_edited(submission, user):
    return submission.is_draft and submission.author == user    
