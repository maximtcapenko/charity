import importlib

imports = {}


def get_module(content_type):
    try:
        key = f'{content_type.app_label}.requirements'
        if not key in imports.keys():
            imports[key] = importlib.import_module(key)
        return imports[key]
    except:
        return None


def file_is_ready_to_be_removed(file, target, content_type):
    module = get_module(content_type)
    if not module:
        return True

    func_name = f'{content_type.model}_file_is_ready_to_be_removed'
    if hasattr(module, func_name):
        func = getattr(module, func_name)
        return func(target, file)
    else:
        return True


def file_is_ready_to_be_added(target, content_type):
    module = get_module(content_type)
    if not module:
        return True
    
    func_name = f'{content_type.model}_file_is_ready_to_be_added'
    if hasattr(module, func_name):
        func = getattr(module, func_name)
        return func(target)
    else:
        return True
