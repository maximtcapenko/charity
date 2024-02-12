from django.forms import Field, Widget
from eav.models import Attribute


class TemplateFieldsWidget(Widget):
    template_name = 'partials/template_fields_list.html'
    fetch_url = ''
    relation_id = ''
    content_type = None

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context['widget']['relation_id'] = self.relation_id
        context['widget']['fetch_url'] = self.fetch_url
        custom_fields = list()

        if self.content_type:
            custom_fields = list(Attribute.objects.filter(
                entity_ct__in=[self.content_type]).all())

            fields = self.content_type.model_class()._meta.fields
            filtered_fields = list(filter(lambda x: x.name in ('name',), fields))
            if filtered_fields:
                for field in filtered_fields:
                    custom_fields.append(field)

        context['widget']['custom_fields'] = custom_fields

        return context


class TemplateFieldsField(Field):
    def __init__(self, relation_id=None, fetch_url=None, **kwargs):
        self.widget = TemplateFieldsWidget
        self.widget.relation_id = relation_id
        self.widget.fetch_url = fetch_url
        super().__init__(**kwargs)

    @property
    def content_type(self):
        return self.widget.content_type

    @content_type.setter
    def content_type(self, content_type):
        self.widget.content_type = content_type
