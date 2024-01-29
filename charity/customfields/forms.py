from copy import deepcopy
from django import forms

from eav.forms import BaseDynamicEntityForm
from eav.models import Attribute, EnumGroup, EnumValue
from commons.forms import FormControlMixin, InitialValidationMixin

from .models import CustomField
from .widgets import ListGroupField


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
    name = forms.CharField(required=True, max_length=50, label='Name')
    field_type = forms.ChoiceField(
        choices=Attribute.DATATYPE_CHOICES, required=True, label='Field Type')

    required = forms.BooleanField(
        required=False, label='Is required', initial=False)
    enum_choices = ListGroupField(required=False)

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
                    self.initial['content_type'],
                    self.cleaned_data['enum_choices'])
            else:

                attribute = self._create_attribute(
                    self.cleaned_data['label'],
                    self.cleaned_data['name'],
                    self.cleaned_data['required'],
                    self.cleaned_data['field_type'],
                    self.initial['content_type'])
            self.instance.attribute = attribute
            self.instance.content_type = self.initial['content_type']
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
        # Reset form fields.
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
