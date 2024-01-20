class DictObjectWrapper(object):
    """
    map dictionary object to wraped dynamic object
    if key: `key1__key2` then it will be mapped to nested object
    with path `key1.key2`
    """

    def __init__(self, dict):
        self.dict = {}
        for key in dict:
            value = dict[key]
            keys = key.split('__')
            DictObjectWrapper._resolve_nested_object(keys, value, self.dict)

    def __getattr__(self, name):
        value = self.dict.get(name)
        if isinstance(value, dict):
            return DictObjectWrapper(value)
        else:
            return value

    @staticmethod
    def _resolve_nested_object(keys, value, dict):
        keys_len = len(keys)
        if keys_len == 0:
            return
         
        item = keys[0]
        if keys_len == 1:
             dict[item] = value
        else:
            if not item in dict.keys():
                dict[item] = {}
        DictObjectWrapper._resolve_nested_object(keys[1:], value, dict[item])

