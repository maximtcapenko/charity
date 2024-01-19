from django import forms

from .functions import get_argument_or_error
from .mixins import FormControlMixin, InitialValidationMixin
from .models import Comment


class CreateCommentForm(
        forms.ModelForm, InitialValidationMixin, FormControlMixin):
    __initial__ = ['target', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialValidationMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.fields['author'].widget = forms.HiddenInput()

        reply = self.initial.get('reply')
        if reply:
            self.fields['reply'].widget = forms.HiddenInput()
        else:
            self.fields.pop('reply')

    def clean(self):
        form_reply = self.cleaned_data.get('reply')

        if form_reply:
            reply = get_argument_or_error('reply', self.initial)
            if form_reply.id != reply.id:
                raise forms.ValidationError(
                    'Reply in form is not the same as target comment')

        return self.cleaned_data

    def save(self):
        self.instance.save()
        self.initial['target'].comments.add(self.instance)
        return self.instance

    class Meta:
        model = Comment
        exclude = ['id', 'tagged_interlocutors']
