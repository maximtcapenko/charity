from django.forms import Field, ValidationError
from django.forms.widgets import Input


class EnumChoicesWidget(Input):
    template_name = 'partials/enum_field_type_input.html'

    def __init__(self, attrs=None, relation_id=None, relation_value=None, enum_values=None):
        super().__init__(attrs)
        self.relation_id = relation_id
        self.relation_value = relation_value
        self.enum_values = enum_values

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget_context = context['widget']
        widget_context['relation_id'] = self.relation_id
        widget_context['relation_value'] = self.relation_value
        widget_context['enum_values'] = self.enum_values
        return context

    def value_from_datadict(self, data, files, name):
        if hasattr(data, 'getlist'):
            return data.getlist(name)
        return data.get(name)


class EAVEnumListGroupField(Field):
    def __init__(self, relation_id=None, relation_value=None, **kwargs):
        self.relation_id = relation_id
        self.relation_value = relation_value
        # widget will be instantiated later in __init__ via super or manually
        super().__init__(**kwargs)
        self.widget = EnumChoicesWidget(
            relation_id=self.relation_id,
            relation_value=self.relation_value
        )

    def to_python(self, value):
        if not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError(
                self.error_messages["invalid_list"], code="invalid_list"
            )
        return [str(val) for val in value]
