class FormControlMixin:

    def __init__(self, *args, **kwargs):
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })