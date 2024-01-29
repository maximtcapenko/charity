from eav.models import Attribute
from django import template
from django.template import loader
from django.utils.safestring import mark_safe

register = template.Library()


class CustomFieldsNode(template.Node):
    templates = {
        Attribute.TYPE_TEXT: 'partials/text_field.html',
        Attribute.TYPE_INT: 'partials/text_field.html',
        Attribute.TYPE_FLOAT: 'partials/text_field.html',
        Attribute.TYPE_DATE: 'partials/date_field.html',
        Attribute.TYPE_BOOLEAN: 'partials/bool_field.html',
        Attribute.TYPE_ENUM: 'partials/text_field.html'
    }

    def __init__(self, instance):
        self.instance = instance

    def render(self, context):
        request = context['request']
        html = ''

        for attribute in self.instance.custom_fields.get_all_attributes():
            template_name = self.templates.get(attribute.datatype)
            if template_name:
                try:
                    value = self.instance.custom_fields.get_value_by_attribute(
                        attribute)
                    html += loader.render_to_string(template_name, {
                        'label': attribute.name,
                        'value': value.value
                    }, request, using=None)
                except:
                    pass

        return mark_safe(html)


@register.inclusion_tag('partials/custom_fields.html', takes_context=True)
def render_custom_fields(context, instance):
    node = CustomFieldsNode(instance)
    return {'fields': node.render(context)}
