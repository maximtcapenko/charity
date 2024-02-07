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


class InitialValidationMixin:
    def __init__(self, *args, **kwargs):
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
            if value:
                resolver = self.__resolvers__.get(field)
                if resolver:
                    queryset = queryset.filter(resolver(value))

        return queryset


class SearchByNameMixin(FormControlMixin):
    min_length = 4

    def __init__(self):
        self.__resolvers__['name'] = lambda field: Q(name__startswith=field)
        self.fields['name'] = forms.CharField(
            max_length=256, min_length=self.min_length,
            required=False, help_text='Search by name', widget=forms.TextInput(attrs={
                'placeholder': 'Search by name',
                'onkeyup': 'javascript:if(this.value.length > %s){this.form.submit()}' % self.min_length
            }))
        
        super().__init__(self)


def require_initial(*args):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
        return wrapper
    return decorator
