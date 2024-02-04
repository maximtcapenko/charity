from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from eav.models import Attribute

from commons.models import Base
from customfields.models import CustomField
from funds.models import Fund


class Operand(models.TextChoices):
    EQ = 'EQ', 'Equals'
    NOT = 'NOT', 'Not'
    GT = 'GT', 'Great then'
    LT = 'LT', 'Less then'


def equals(eav_config, attribute, values):
    if len(values) > 1:
        return Q(**{f'{eav_config.eav_attr}__{attribute.slug}__in': [value.get_value(attribute) for value in values]})

    return Q(**{f'{eav_config.eav_attr}__{attribute.slug}': values[0].get_value(attribute)})


def not_equals(eav_config, attribute, values):
    return ~equals(eav_config, attribute, values)


def gt(eav_config, attribute, values):
    return Q(**{f'{eav_config.eav_attr}__{attribute.slug}__gt': values[0].get_value(attribute)})


def lt(eav_config, attribute, values):
    return Q(**{f'{eav_config.eav_attr}__{attribute.slug}__lt': values[0].get_value(attribute)})


all_operands = (Operand.EQ,
                Operand.NOT,
                Operand.GT,
                Operand.LT)


TYPE_OPERAND_MAPPING = {
    Attribute.TYPE_INT: all_operands,
    Attribute.TYPE_FLOAT: all_operands,
    Attribute.TYPE_ENUM: (
        Operand.EQ,
        Operand.NOT),
    Attribute.TYPE_TEXT: (
        Operand.EQ,
        Operand.NOT),
    Attribute.TYPE_BOOLEAN: (
        Operand.EQ,
        Operand.NOT),
    Attribute.TYPE_DATE: all_operands
}

OPERAND_MAPPING = {
    Operand.EQ: equals,
    Operand.NOT: not_equals,
    Operand.GT: gt,
    Operand.LT: lt
}


class Filter(Base):
    name = models.CharField(max_length=256)
    notes = models.TextField()
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT, related_name='filters')
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)


class Expression(Base):
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE,
                               related_name='expressions')
    field = models.ForeignKey(CustomField, on_delete=models.PROTECT)
    operand = models.CharField(choices=Operand.choices, max_length=10)

    @property
    def is_searchable(self):
        return self.field.is_searchable

    def get_expression(self, model):
        if not  hasattr(model, '_eav_config_cls'):
            return None
        
        operand = OPERAND_MAPPING.get(self.operand)
        return operand(model._eav_config_cls(), self.field.attribute, self.values.all())


class ExpressionValue(Base):
    expression = models.ForeignKey(
        Expression, on_delete=models.CASCADE, related_name='values')
    value_bool = models.BooleanField(blank=True, null=True)
    value_date = models.DateTimeField(blank=True, null=True)
    value_float = models.FloatField(blank=True, null=True)
    value_int = models.BigIntegerField(blank=True, null=True)
    value_text = models.TextField(blank=True, null=True)
    value_enum = models.CharField(max_length=50, blank=True, null=True)

    def get_value(self, attribute):
        return getattr(self, 'value_{0}'.format(attribute.datatype))

    def set_value(self, attribute, new_value):
        setattr(self, 'value_{0}'.format(attribute.datatype), new_value)

    @property
    def value(self):
        return self.get_value(self.expression.field.attribute)

    @value.setter
    def value(self, value):
        self.set_value(self.expression.field.attribute, value)