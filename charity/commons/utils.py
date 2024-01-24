from django.core.paginator import Page
from django.db.models import fields


class DictObjectWrapper(object):
    class DynamicObject:
        pass

    @staticmethod
    def _file_field_value_getter(field, value):
        if not issubclass(field.__class__, fields.files.FileField):
            return None

        field.storage
        instance = DictObjectWrapper.DynamicObject()
        instance.url = field.storage.url(value)
        return instance

    field_value_getters = [
        _file_field_value_getter
    ]

    """
    map dictionary object to wraped dynamic object
    if key: `key1__key2` then it will be mapped to nested object
    with path `key1.key2`
    """

    def __init__(self, dict, is_init=False, model=None):
        self.model = model
        if is_init:
            self.dict = dict
        else:
            self.dict = {}
            for key in dict:
                value = dict[key]
                keys = key.split('__')
                DictObjectWrapper._resolve_nested_object(
                    keys, value, self.dict)

    def __getattr__(self, name):
        value = self.dict.get(name)

        if isinstance(value, dict):
            model = None
            if self.model:
                field = self.model._meta.get_field(name)
                if field.is_relation:
                    model = field.related_model

            return DictObjectWrapper(value, is_init=True, model=model)
        else:
            if self.model:
                try:
                    field = self.model._meta.get_field(name)
                    if field:
                        for getter in DictObjectWrapper.field_value_getters:
                            instance = getter(field, value)
                            if instance:
                                return instance
                except:
                    pass

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


class WrappedPage(Page):
    def __init__(self, page, model=None):
        self.model = model
        super().__init__(page.object_list, page.number, page.paginator)

    def __getitem__(self, item):
        item = super().__getitem__(item)

        if isinstance(item, dict):
            return DictObjectWrapper(item, model=self.model)
        else:
            return item
