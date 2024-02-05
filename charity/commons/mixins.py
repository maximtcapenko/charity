from functools import wraps

from django import forms
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


def require_initial(*args):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
        return wrapper
    return decorator
