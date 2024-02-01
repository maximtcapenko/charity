from django import forms


class CustomLabeledModelChoiceField(forms.ModelChoiceField):
    def __init__(self, lable_func, *args, **kwargs):
        self.lable_func = lable_func
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        if self.lable_func:
            return self.lable_func(obj)

        return super().label_from_instance(obj)
