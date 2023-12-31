from django import forms


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
            elif (isinstance(self.fields[field], forms.ModelChoiceField)):
                self.fields[field].empty_label = '%s %s' % (
                    'Select', self.fields[field].label)
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })

            else:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
