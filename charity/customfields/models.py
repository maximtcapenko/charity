from django.forms import fields, widgets, Form
from django.db import models
from django.contrib.contenttypes.models import ContentType

from commons.models import Base
from funds.models import Fund


class CustomField(Base):
    field_config = models.JSONField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)


form_fields = {
    'TextBox': {
        'field': fields.CharField
    },
    'CheckBox': {
        'field': fields.BooleanField
    },
    'TextArea': {
        'field': fields.CharField,
        'widget': widgets.Textarea
    },
    'Number': {
        'field': fields.IntegerField
    },
    'Decimal': {
        'field': fields.DecimalField
    },
    'DatePicker': {
        'field': fields.DateField
    },
    'Choices': {
        'field': fields.ChoiceField,
        'choices': []
    }
}


class DynamicFormBuilder(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__


class DynamicForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
