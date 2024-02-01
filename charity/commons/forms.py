from django import forms

from funds.models import Fund

from .functions import get_argument_or_error, resolve_many_2_many_attr, resolve_rel_attr_path
from .mixins import FormControlMixin, InitialValidationMixin
from .models import Comment


class CreateCommentForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['target_id', 'target_content_type', 'author', 'fund']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['author'].widget = forms.HiddenInput()
        self.fields['notes'].label = False

        reply = self.initial.get('reply')

        if reply:
            self.fields['reply'].widget = forms.HiddenInput()
        else:
            self.fields.pop('reply')

    def clean(self):
        content_type = self.initial['target_content_type']
        fund_attr_path = resolve_rel_attr_path(
            Fund, content_type.model_class())

        """Check if author and commented item are in the same fund"""
        filter = {
            fund_attr_path: self.initial['fund'],
            'pk': self.initial['target_id']
        }

        if not content_type.model_class().objects.filter(**filter).exists():
            raise forms.ValidationError(
                'Author does not have access to commented object')

        form_reply = self.cleaned_data.get('reply')
        if form_reply:
            reply = get_argument_or_error('reply', self.initial)
            if form_reply.id != reply.id:
                raise forms.ValidationError(
                    'Reply in form is not the same as target comment')

        return self.cleaned_data

    def save(self):
        self.instance.save()
        comments = resolve_many_2_many_attr(Comment,
            self.initial['target_content_type'], self.initial['target_id'])
        comments.add(self.instance)
        return self.instance

    class Meta:
        model = Comment
        exclude = ['id', 'tagged_interlocutors']


class CustomLabeledModelChoiceField(forms.ModelChoiceField):
    def __init__(self, lable_func, *args, **kwargs):
        self.lable_func = lable_func
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        if self.lable_func:
            return self.lable_func(obj)

        return super().label_from_instance(obj)
