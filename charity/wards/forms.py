from django import forms
from django.db.models import Exists, OuterRef

from commons.mixins import FormControlMixin, SearchByNameMixin, SearchFormMixin

from filters.models import Filter

from customfields.forms import BaseCustomFieldsModelForm
from tasks.models import Task

from .models import Ward


class CreateWardForm(BaseCustomFieldsModelForm, FormControlMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FormControlMixin.__init__(self)

        self.fields['fund'].widget = forms.HiddenInput()

    class Meta:
        model = Ward
        exclude = ['id', 'attachments', 'cover', 'comments']


class SearchWardForm(forms.Form, FormControlMixin, SearchByNameMixin, SearchFormMixin):
    __resolvers__ = {}

    in_work_only = forms.BooleanField(label='In work', required=False)

    def __init__(self, fund, *args, **kwargs):
        super().__init__(*args, **kwargs)
        SearchByNameMixin.__init__(self)
        filter = forms.ModelChoiceField(queryset=Filter.objects.filter(
            fund=fund, content_type__model='ward'), required=False, label='Filter')
        filter.widget.attrs.update({
            'onchange': 'javascript:this.form.submit()'
        })
        self.fields['filter'] = filter
        self.fields['in_work_only'].widget.attrs.update({
            'onchange': 'javascript:this.form.submit()'
        })

        self.__resolvers__['filter'] = self.apply_customfields_filter
        self.__resolvers__['in_work_only'] = lambda field: Exists(Task.objects.filter(ward=OuterRef('pk')))

        FormControlMixin.__init__(self)

    def apply_customfields_filter(self, filter):
        search_fields = filter.expressions.filter(
            field__is_searchable=True).all()
        return [field.get_expression(Ward) for field in search_fields]
