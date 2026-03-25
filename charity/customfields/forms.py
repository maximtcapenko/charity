from copy import deepcopy
import re
from django import forms
from django.utils.translation import gettext_lazy as _

from eav.forms import BaseDynamicEntityForm
from eav.models import Attribute, EnumGroup, EnumValue

from commons.mixins import FormControlMixin, InitialMixin

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
    if re.search(r'\s', value):
        raise forms.ValidationError(
            _('Name of the field cannot contain white spaces.'))


class CustomFieldCreateForm(forms.ModelForm, InitialMixin, FormControlMixin):
    __initial__ = ['fund', 'content_type']

    field_order = ['label', 'name', 'field_type', 'required']

    label = forms.CharField(required=True, max_length=50, label=_('Label'))
    name = forms.CharField(required=True, max_length=50,
                           label=_('Name'), validators=[validate_field_name])
    field_type = forms.ChoiceField(
        choices=DATATYPE_CHOICES, required=True, label=_('Field Type'))

    required = forms.BooleanField(
        required=False, label=_('Is required'), initial=False)
    enum_choices = EAVEnumListGroupField(
        required=False, 
        relation_id='id_field_type', 
        relation_value=Attribute.TYPE_ENUM,
        label=_('Choices')
    )

    class Meta:
        model = CustomField
        exclude = ['id', 'date_created', 'attribute', 'content_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)

        self.form.fund.widget = forms.HiddenInput()

        if not self.instance._state.adding:
            attr = getattr(self.instance, 'attribute', None)
            if attr:
                self.fields['name'].initial = attr.slug
                self.fields['name'].disabled = True
                self.fields['label'].initial = attr.name
                self.fields['field_type'].initial = attr.datatype
                self.fields['field_type'].disabled = True
                self.fields['required'].initial = attr.required
                
                if attr.datatype == Attribute.TYPE_ENUM and attr.enum_group:
                    self.fields['enum_choices'].widget.enum_values = attr.enum_group.values.all()

        FormControlMixin.__init__(self)

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if not instance.attribute_id:
            label = self.cleaned_data['label']
            name = self.cleaned_data['name']
            required = self.cleaned_data['required']
            field_type = self.cleaned_data['field_type']
            choices = self.cleaned_data.get('enum_choices', [])

            if field_type == Attribute.TYPE_ENUM:
                instance.attribute = self._create_enum_attribute(label, name, required, choices)
            else:
                instance.attribute = self._create_attribute(label, name, required, field_type)
            
            instance.content_type = self.content_type
        else:
            instance.attribute.name = self.cleaned_data['label']
            instance.attribute.required = self.cleaned_data['required']
            instance.attribute.save()

        if commit:
            instance.save()
        return instance

    def _create_attribute(self, label, name, required, field_type):
        attr = Attribute.objects.create(
            name=label,
            slug=name,
            datatype=field_type,
            required=required)
        attr.entity_ct.add(self.content_type)
        return attr

    def _create_enum_attribute(self, label, name, required, values):
        if not values:
            return None
        
        group, _ = EnumGroup.objects.get_or_create(name=name)
        for val in values:
            enum_val, _ = EnumValue.objects.get_or_create(value=val)
            if not group.values.filter(pk=enum_val.pk).exists():
                group.values.add(enum_val)

        attr = Attribute.objects.create(
            name=label,
            slug=name,
            required=required,
            datatype=Attribute.TYPE_ENUM,
            enum_group=group)
        attr.entity_ct.add(self.content_type)
        return attr


class BaseCustomFieldsModelForm(BaseDynamicEntityForm):
    FIELD_CLASSES = {
        Attribute.TYPE_TEXT: forms.CharField,
        Attribute.TYPE_FLOAT: forms.FloatField,
        Attribute.TYPE_INT: forms.IntegerField,
        Attribute.TYPE_DATE: forms.DateField,
        Attribute.TYPE_BOOLEAN: forms.BooleanField,
        Attribute.TYPE_ENUM: forms.ChoiceField,
    }

    def _build_dynamic_fields(self):
        # We start with the base_fields
        self.fields = deepcopy(self.base_fields)

        for attribute in self.entity.get_all_attributes():
            value = getattr(self.entity, attribute.slug, None)

            defaults = {
                'label': attribute.name.capitalize(),
                'required': attribute.required,
                'help_text': attribute.help_text,
                'validators': attribute.get_validators(),
            }

            if attribute.datatype == Attribute.TYPE_ENUM:
                choices = [('', f'Select {attribute.name}')]
                choices += list(attribute.get_choices().values_list('id', 'value'))
                defaults.update({'choices': choices})
                if value:
                    defaults.update({'initial': value.pk})
            elif attribute.datatype == Attribute.TYPE_OBJECT:
                continue
            else:
                if value:
                    defaults.update({'initial': value})

            FieldClass = self.FIELD_CLASSES.get(attribute.datatype, forms.CharField)
            self.fields[attribute.slug] = FieldClass(**defaults)
