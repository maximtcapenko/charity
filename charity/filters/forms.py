from django import forms
from django.db.models import Q, Exists, OuterRef
from django.urls import reverse

from eav.models import Attribute

from commons.forms import CustomLabeledModelChoiceField
from commons.mixins import FormControlMixin, InitialMixin
from customfields.forms import DATATYPE_DICT, BaseCustomFieldsModelForm

from .models import TYPE_OPERAND_MAPPING, Expression, Filter, ExpressionValue
from .widgets import ExpressionFieldValue


class CreateFilterForm(
        forms.ModelForm,
        InitialMixin, FormControlMixin):
    __initial__ = ['fund', 'author', 'content_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)
        FormControlMixin.__init__(self)

    def save(self):
        self.instance.fund = self.fund
        self.instance.author = self.author
        self.instance.content_type = self.content_type
        self.instance.save()

        return self.instance

    class Meta:
        model = Filter
        exclude = ['id', 'date_created', 'fund', 'author', 'content_type']


class CreateFilterExpressionForm(
        forms.ModelForm,
        InitialMixin, FormControlMixin):
    __initial__ = ['fund', 'filter']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        fund = self.initial['fund']
        filter = self.initial['filter']

        self.form.field = CustomLabeledModelChoiceField(queryset=fund.custom_fields.filter(
            Q(is_searchable=True) &
            ~Exists(Expression.objects.filter(filter=filter, field=OuterRef('pk')))),
            label_func=lambda field: f'{field.attribute.name} ({DATATYPE_DICT[field.attribute.datatype]})',
            label='Field', required=True)

        self.form.operand = forms.CharField(
            max_length=10, widget=forms.HiddenInput(), required=True)
        self.form.value = ExpressionFieldValue(relation_id='id_field', operand_id='id_operand', fetch_url=reverse(
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


class AddExpressionValueForm(
        forms.Form, InitialMixin, FormControlMixin):
    __initial__ = ['expression']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        expression = self.expression
        attribute = expression.field.attribute
        field = BaseCustomFieldsModelForm.FIELD_CLASSES.get(
            attribute.datatype)()

        if attribute.datatype == Attribute.TYPE_ENUM:
            values = attribute.get_choices().values_list('value', 'value')
            choices = [('', f'Select {attribute.name}')] + list(values)
            field.choices = choices
        elif attribute.datatype == Attribute.TYPE_DATE:
            field.widget.attrs.update({'type': 'date'})

        self.form.value = field

        FormControlMixin.__init__(self)

    
    def save(self):
        instance = ExpressionValue(expression=self.expression)
        value = self.cleaned_data['value']
        instance.value = value
        instance.save()
        
        return instance
