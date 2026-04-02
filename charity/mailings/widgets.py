from django.forms import Field, Widget
from eav.models import Attribute


class TemplateFieldsWidget(Widget):
    template_name = 'partials/template_fields_list.html'

    def __init__(self, attrs=None, relation_id=None, fetch_url=None, content_type=None):
        super().__init__(attrs)
        self.relation_id = relation_id
        self.fetch_url = fetch_url
        self.content_type = content_type

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget_context = context['widget']
        widget_context['relation_id'] = self.relation_id
        widget_context['fetch_url'] = self.fetch_url

        custom_fields = []
        if self.content_type:
            # Fetch EAV attributes
            custom_fields.extend(Attribute.objects.filter(
                entity_ct=self.content_type
            ))

            # Fetch specific model fields (e.g., 'name')
            model_class = self.content_type.model_class()
            if model_class:
                fields = model_class._meta.fields
                custom_fields.extend([f for f in fields if f.name in model_class.__rendered_fields__])

        widget_context['custom_fields'] = custom_fields
        return context


class TemplateFieldsField(Field):
    def __init__(self, relation_id=None, fetch_url=None, **kwargs):
        kwargs['widget'] = TemplateFieldsWidget(
            relation_id=relation_id,
            fetch_url=fetch_url
        )
        super().__init__(**kwargs)

    @property
    def content_type(self):
        return self.widget.content_type

    @content_type.setter
    def content_type(self, value):
        self.widget.content_type = value
