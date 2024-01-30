from django.forms import Field, ValidationError
from django.forms.widgets import Input


class FieldTypeWidget(Input):
    template_name = 'partials/enum_field_type_input.html'
    relation_id = None
    relation_value = None
    attribute = None

    def __init__(
            self, attrs=None):
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context['widget']['relation_id'] = self.relation_id
        context['widget']['relation_value'] = self.relation_value

        if self.attribute and self.attribute.enum_group:
            context['widget']['enum_values'] = self.attribute.enum_group.values.all()

        return context

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)


class EAVEnumListGroupField(Field):
    def __init__(
            self,
            relation_id=None,
            relation_value=None, **kwargs):
        self.widget = FieldTypeWidget
        self.widget.relation_id = relation_id
        self.widget.relation_value = relation_value
        super().__init__(**kwargs)

    @property
    def attribute(self):
        return self.widget.attribute

    @attribute.setter
    def attribute(self, attribute):
        self.widget.attribute = attribute

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(
                self.error_messages["invalid_list"], code="invalid_list"
            )
        return [str(val) for val in value]
