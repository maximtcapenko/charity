def ward_file_is_ready_to_be_removed(ward, file):
    return not ward.tasks.filter(is_started=True, is_done=False).exists()


def ward_file_is_ready_to_be_added(ward):
    return not ward.tasks.filter(is_started=True, is_done=False).exists()
