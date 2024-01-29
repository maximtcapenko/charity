from django.forms import Field, ValidationError
from django.forms.widgets import Input


class FieldTypeWidget(Input):
    template_name = 'partials/enum_field_type_input.html'

    def __init__(self, attrs=None, attribute=None):
        super().__init__(attrs)
        self.attribute = attribute

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.attribute and self.attribute.enum_group:
            context['widget']['enum_values'] = self.attribute.enum_group.values.all()
        return context

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)


class ListGroupField(Field):
    def __init__(self, attribute=None, **kwargs):
        self.widget = FieldTypeWidget
        self._attribute = attribute
        super().__init__(**kwargs)

    @property
    def attribute(self):
        return self._attribute

    @attribute.setter
    def attribute(self, attribute):
        self._attribute = attribute
        self.widget.attribute = attribute

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(
                self.error_messages["invalid_list"], code="invalid_list"
            )
        return [str(val) for val in value]
