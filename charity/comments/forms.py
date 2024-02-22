from django import forms
from funds.models import Fund

from commons.functional import get_argument_or_error, resolve_many_2_many_attr_path, \
    resolve_rel_attr_path
from commons.mixins import FormControlMixin, InitialMixin

from .models import Comment


class CreateCommentForm(
        forms.ModelForm, InitialMixin, FormControlMixin):
    __initial__ = ['target', 'target_content_type', 'author', 'fund']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        InitialMixin.__init__(self)
        FormControlMixin.__init__(self)

        self.form.author.widget = forms.HiddenInput()
        self.form.notes.label = False

        reply = self.initial.get('reply')

        if reply:
            self.fields['reply'].widget = forms.HiddenInput()
        else:
            self.fields.pop('reply')

    def clean(self):
        content_type = self.target_content_type
        fund_attr_path = resolve_rel_attr_path(
            Fund, content_type.model_class())

        """Check if author and commented item are in the same fund"""
        filter = {
            fund_attr_path: self.fund,
            'pk': self.target.pk
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
        target_attr = resolve_many_2_many_attr_path(
            Comment, self.target_content_type.model_class())

        comments = getattr(self.target, target_attr)
        comments.add(self.instance)
        return self.instance

    class Meta:
        model = Comment
        exclude = ['id', 'tagged_interlocutors']
