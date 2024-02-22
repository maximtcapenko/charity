from commons.functional import get_requirements_module


def comment_is_ready_to_be_removed(file, target, content_type):
    module = get_requirements_module(content_type)
    if not module:
        return True

    func_name = f'{content_type.model}_comment_is_ready_to_be_removed'
    if hasattr(module, func_name):
        func = getattr(module, func_name)
        return func(target, file)
    else:
        return True


def comment_is_ready_to_be_added(target, content_type):
    module = get_requirements_module(content_type)
    if not module:
        return True

    func_name = f'{content_type.model}_comment_is_ready_to_be_added'
    if hasattr(module, func_name):
        func = getattr(module, func_name)
        return func(target)
    else:
        return True
