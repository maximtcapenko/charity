from typing import Any
from django import forms
from django.db.models import Q, Exists, OuterRef
from django.urls import reverse

from commons.forms import CustomLabeledModelChoiceField
from commons.mixins import FormControlMixin, InitialValidationMixin
from customfields.forms import DATATYPE_DICT

from .models import TYPE_OPERAND_MAPPING, Expression, Filter, ExpressionValue
from .widgets import ExpressionFieldValue


class CreateFilterForm(
        forms.ModelForm,
        InitialValidationMixin, FormControlMixin):
    __initial__ = ['fund', 'author', 'content_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

    def save(self):
        self.instance.fund = self.initial['fund']
        self.instance.author = self.initial['author']
        self.instance.content_type = self.initial['content_type']
        self.instance.save()

        return self.instance

    class Meta:
        model = Filter
        exclude = ['id', 'date_created', 'fund', 'author', 'content_type']


class CreateFilterExpressionForm(
        forms.ModelForm,
        InitialValidationMixin, FormControlMixin):
    __initial__ = ['fund', 'filter']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)

        fund = self.initial['fund']
        filter = self.initial['filter']

        self.fields['field'] = CustomLabeledModelChoiceField(queryset=fund.custom_fields.filter(
            Q(is_searchable=True) &
            ~Exists(Expression.objects.filter(filter=filter, field=OuterRef('pk')))),
            lable_func=lambda field: f'{field.attribute.name} ({DATATYPE_DICT[field.attribute.datatype]})',
            label='Field', required=True)

        self.fields['operand'] = forms.CharField(
            max_length=10, widget=forms.HiddenInput(), required=True)
        self.fields['value'] = ExpressionFieldValue(relation_id='id_field', operand_id='id_operand', fetch_url=reverse(
            'filters:get_filed_value_input_details'), label=False)

        FormControlMixin.__init__(self)

    def clean(self):
        operand = self.cleaned_data['operand']
        attribute = self.cleaned_data['field'].attribute
        available_operands = TYPE_OPERAND_MAPPING.get(attribute.datatype)

        if operand not in available_operands:
            raise forms.ValidationError('Incorrect value of operand')

        return self.cleaned_data

    def save(self):
        self.instance.filter = self.initial['filter']
        self.instance.save()

        value = self.cleaned_data['value']
        attribute = self.cleaned_data['field'].attribute
        expressionValue = ExpressionValue()
        expressionValue.expression = self.instance
        expressionValue.set_value(attribute, value)
        expressionValue.save()

        return self.instance

    class Meta:
        model = Expression
        exclude = ('id', 'date_created', 'filter')
