from functools import wraps

from django import forms


class FileUploadMixin:
    pass


class FormControlMixin:
    def __init__(self, *args, **kwargs):
        for field in iter(self.fields):
            if (isinstance(self.fields[field].widget, forms.CheckboxInput)):
                self.fields[field].widget.attrs.update({
                    'class': 'form-check-input'
                })
            elif (isinstance(self.fields[field].widget, forms.DateInput)):
                self.fields[field].widget = forms.DateInput(
                    attrs={'type': 'date', 'class': 'form-control'})
            elif (isinstance(self.fields[field].widget, forms.DateTimeInput)):
                self.fields[field].widget = forms.DateTimeInput(
                    attrs={'type': 'date', 'class': 'form-control'})
            elif (isinstance(self.fields[field], forms.ModelChoiceField)):
                self.fields[field].empty_label = '%s %s' % (
                    'Select', self.fields[field].label)
                self.fields[field].widget.attrs.update({
                    'class': 'form-select'
                })

            else:
                self.fields[field].widget.attrs.update({
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
