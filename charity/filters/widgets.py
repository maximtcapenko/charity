from django.template import loader
from django.utils.safestring import mark_safe
from django.forms import Field
from django.forms.widgets import Input

from eav.models import Attribute

from customfields.forms import BaseCustomFieldsModelForm

from .models import TYPE_OPERAND_MAPPING


class ExpressionValueWidget(Input):
    template_name = 'partials/expression_value_input.html'
    fetch_url = ''
    relation_id = ''
    operand_id = ''

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context['widget']['relation_id'] = self.relation_id
        context['widget']['fetch_url'] = self.fetch_url
        context['widget']['operand_id'] = self.operand_id

        return context

    @staticmethod
    def get_rendered_value_widget(request, custom_field):
        template_name = 'partials/expression_value_input_details.html'
        attribute = custom_field.attribute
        available_operands = TYPE_OPERAND_MAPPING.get(attribute.datatype)

        field = BaseCustomFieldsModelForm.FIELD_CLASSES.get(attribute.datatype)

        if attribute.datatype == Attribute.TYPE_ENUM:
            values = attribute.get_choices().values_list('value', 'value')
            choices = [('', f'Select {attribute.name}')] + list(values)
            input = field.widget(
                attrs={'class': 'form-select'}, choices=choices).render('value', None)
        elif attribute.datatype == Attribute.TYPE_DATE:
            input = field.widget(
                attrs={'class': 'form-control', 'type': 'date'}).render('value', None)
        elif attribute.datatype == Attribute.TYPE_BOOLEAN:
            field.widget.template_name = 'partials/form-switch.html'
            input = field.widget({
                'class': 'form-check-input'}).render('value', None)
        else:
            input = field.widget(
                attrs={'class': 'form-control'}).render('value', None)

        html = loader.render_to_string(template_name, {
            'available_operands': available_operands,
            'input': mark_safe(input)
        }, request, using=None)

        return {'html': html}


class ExpressionFieldValue(Field):
    def __init__(
            self,
            relation_id=None,
            fetch_url=None,
            attr_resolver=None,
            operand_id=None, **kwargs):
        self.attr_resolver = attr_resolver
        self.widget = ExpressionValueWidget
        self.widget.relation_id = relation_id
        self.widget.fetch_url = fetch_url
        self.widget.operand_id = operand_id
        super().__init__(**kwargs)

    def to_python(self, value):
        attribute = self.attr_resolver()
        return BaseCustomFieldsModelForm.FIELD_CLASSES.get(
            attribute.datatype)().to_python(value)
