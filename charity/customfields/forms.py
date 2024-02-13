from copy import deepcopy
from django import forms
from django.utils.translation import gettext_lazy as _

from eav.forms import BaseDynamicEntityForm
from eav.models import Attribute, EnumGroup, EnumValue
from commons.mixins import FormControlMixin, InitialValidationMixin

from .models import CustomField
from .widgets import EAVEnumListGroupField


DATATYPE_CHOICES = (
    (Attribute.TYPE_TEXT, _('Text')),
    (Attribute.TYPE_DATE, _('Date')),
    (Attribute.TYPE_FLOAT, _('Float')),
    (Attribute.TYPE_INT, _('Integer')),
    (Attribute.TYPE_BOOLEAN, _('True / False')),
    (Attribute.TYPE_ENUM, _('Multiple Choice')),
)

DATATYPE_DICT = {
    Attribute.TYPE_TEXT: _('Text'),
    Attribute.TYPE_DATE: _('Date'),
    Attribute.TYPE_FLOAT: _('Float'),
    Attribute.TYPE_INT: _('Integer'),
    Attribute.TYPE_BOOLEAN: _('True / False'),
    Attribute.TYPE_ENUM: _('Multiple Choice'),
}

def validate_field_name(value):
    import re
    match = re.match('^(.*\s+.*)+$', value)
    if match is not None:
        raise forms.ValidationError(
            _('Name of the field cannot contain white spaces.'))


class CustomFieldCreateForm(forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['fund', 'content_type']

    field_order = ['label', 'name', 'field_type', 'required']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['fund'].widget = forms.HiddenInput()
        if self.instance.attribute_id:
            self.fields['name'].initial = self.instance.attribute.slug
            self.fields['name'].disabled = True
            self.fields['label'].initial = self.instance.attribute.name
            self.fields['field_type'].initial = self.instance.attribute.datatype
            self.fields['field_type'].disabled = True
            self.fields['required'].initial = self.instance.attribute.required
            self.fields['enum_choices'].attribute = self.instance.attribute

        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

    label = forms.CharField(required=True, max_length=50, label='Label')
    name = forms.CharField(required=True, max_length=50,
                           label='Name', validators=[validate_field_name])
    field_type = forms.ChoiceField(
        choices=DATATYPE_CHOICES, required=True, label='Field Type')

    required = forms.BooleanField(
        required=False, label='Is required', initial=False)
    enum_choices = EAVEnumListGroupField(
        required=False, relation_id='id_field_type', relation_value=Attribute.TYPE_ENUM)

    class Meta:
        model = CustomField
        exclude = ['id', 'date_created', 'attribute', 'content_type']

    def save(self):
        if not self.instance.attribute_id:
            if self.cleaned_data['field_type'] == Attribute.TYPE_ENUM:
                attribute = self._create_enum_attribute(
                    self.cleaned_data['label'],
                    self.cleaned_data['name'],
                    self.cleaned_data['required'],
                    self.content_type,
                    self.cleaned_data['enum_choices'])
            else:
                attribute = self._create_attribute(
                    self.cleaned_data['label'],
                    self.cleaned_data['name'],
                    self.cleaned_data['required'],
                    self.cleaned_data['field_type'],
                    self.content_type)
            self.instance.attribute = attribute
            self.instance.content_type = self.content_type
        else:
            self.instance.attribute.name = self.cleaned_data['label']
            self.instance.attribute.required = self.cleaned_data['required']
            self.instance.attribute.save()

        self.instance.save()

        return self.instance

    def _create_attribute(self, label, name, required, field_type, entity):
        attr = Attribute.objects.create(
            name=label,
            slug=name,
            datatype=field_type,
            required=required)

        attr.entity_ct.add(entity)
        return attr

    def _create_enum_attribute(self, label, name, required, entity, values):
        if len(values) == 0:
            return None
        group, result = EnumGroup.objects.get_or_create(name=name)

        for enum in values:
            value, result = EnumValue.objects.get_or_create(value=enum)
            if not group.values.filter(value=value).exists():
                group.values.add(value)

        attr = Attribute.objects.create(
            name=label,
            slug=name,
            required=required,
            datatype=Attribute.TYPE_ENUM,
            enum_group=group)

        attr.entity_ct.add(entity)
        return attr


class BaseCustomFieldsModelForm(BaseDynamicEntityForm):
    FIELD_CLASSES = {
        'text': forms.CharField,
        'float': forms.FloatField,
        'int': forms.IntegerField,
        'date': forms.DateField,
        'bool': forms.BooleanField,
        'enum': forms.ChoiceField,
    }

    def _build_dynamic_fields(self):
        self.fields = deepcopy(self.base_fields)

        for attribute in self.entity.get_all_attributes():
            value = getattr(self.entity, attribute.slug)

            defaults = {
                'label': attribute.name.capitalize(),
                'required': attribute.required,
                'help_text': attribute.help_text,
                'validators': attribute.get_validators(),
            }

            datatype = attribute.datatype

            if datatype == attribute.TYPE_ENUM:
                values = attribute.get_choices().values_list('id', 'value')
                choices = [('', f'Select {attribute.name}')] + list(values)
                defaults.update({'choices': choices})

                if value:
                    defaults.update({'initial': value.pk})

            elif datatype == attribute.TYPE_OBJECT:
                continue

            MappedField = self.FIELD_CLASSES[datatype]
            self.fields[attribute.slug] = MappedField(**defaults)

            # Fill initial data (if attribute was already defined).
            if value and not datatype == attribute.TYPE_ENUM:
                self.initial[attribute.slug] = value
