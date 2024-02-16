from django import forms
from django.db.models import Q
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe


class DivErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''

        result = ''
        for error in self:
            result += f'<div class="alert alert-dismissible fade show alert-danger" \
                  role="alert"><i class="fa-solid fa-triangle-exclamation"></i> \
                  {error}<button type="button" class="btn-close" \
                  data-bs-dismiss="alert" aria-label="Close"></button></div>'

        return mark_safe(result)


class FileUploadMixin:
    pass


class FormControlMixin:
    def __init__(self, *args, **kwargs):
        self.error_class = DivErrorList

        for field_name in self.fields:
            field = self.fields[field_name]
            if not hasattr(field, 'widget'):
                continue

            if (isinstance(field.widget, forms.CheckboxInput)):
                field.widget.template_name = 'partials/form-switch.html'
                field.widget.attrs.update({
                    'label': field.label,
                    'class': 'form-check-input'
                })
                field.label = False
            elif (isinstance(field.widget, forms.DateInput)):
                field.widget = forms.DateInput(
                    attrs={'type': 'date', 'class': 'form-control'})
            elif (isinstance(field.widget, forms.DateTimeInput)):
                field.widget = forms.DateTimeInput(
                    attrs={'type': 'date', 'class': 'form-control'})
            elif (isinstance(field, forms.ChoiceField)):
                field.empty_label = '%s %s' % ('Select', field.label)
                field.widget.attrs.update({
                    'class': 'form-select'
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control'
                })


class FormFieldsWrapper:
    def __init__(self, fields):
        self._fields = fields

    def __getattr__(self, name):
        if name not in self._fields:
            raise AttributeError(f'Form does not contain attribute {name}')

        field = self._fields[name]
        field.name = name
        return field

    def __setattr__(self, name, value):
        if name == '_fields':
            self.__dict__[name] = value
        else:
            self._fields[name] = value


class FormFieldsWrapperMixin:
    def __init__(self):
        self.form = FormFieldsWrapper(self.fields)


class InitialMixin(FormFieldsWrapperMixin):
    def __getattr__(self, name):
        if name in self.__initial__:
            return self.initial[name]
        else:
            raise AttributeError(f'Attribute {name} does not exists.')

    def __init__(self):
        super().__init__()
        if not hasattr(self, '__initial__'):
            raise ValueError(
                'Form requires initial fields, but __initial__ is not defined')

        params = []

        for field in self.__initial__:
            '''validate each required field'''
            if not self.initial.get(field):
                params.append(field)

        if len(params) > 0:
            raise ValueError(f'Missing required parameters: {params}')


class SearchFormMixin:
    def get_search_queryset(self, queryset):
        self.full_clean()
        for field in self.fields:
            value = self.cleaned_data.get(field)
            resolver = self.__resolvers__.get(field)
            if resolver and value:
                filter = resolver(value)
                if hasattr(filter, '__iter__'):
                    for expression in filter:
                        queryset = queryset.filter(expression)
                else:
                    queryset = queryset.filter(filter)

        return queryset


class SearchByNameMixin:
    min_length = 4

    def __init__(self):
        self.__resolvers__['name'] = lambda field: Q(name__startswith=field)
        widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name'
        })
        widget.template_name = 'partials/search-box.html'
        self.fields['name'] = forms.CharField(
            max_length=256, min_length=self.min_length,
            required=False, help_text='Search by name', widget=widget)
