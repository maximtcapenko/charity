from django import forms
from django.db import models
from django.contrib.auth.models import User

from commons.functional import get_reviewer_label
from commons.forms import CustomLabeledModelChoiceField, DateRangeField
from commons.widgets import DateRangeWidget
from commons.mixins import FormControlMixin, SearchByNameMixin, SearchFormMixin

from .models import History


class SearchHistoryForm(forms.Form, FormControlMixin, SearchFormMixin, SearchByNameMixin):
    date_range = DateRangeField(
        date_format='%Y-%m-%d',
        required=False,
        widget=DateRangeWidget(date_format='YYYY-MM-DD')
    )

    def __init__(self, fund, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__resolvers__ = {}

        SearchByNameMixin.__init__(self)
        self.fields['author'] = CustomLabeledModelChoiceField(queryset=User.objects.select_related(
            'volunteer_profile').filter(
            models.Q(volunteer_profile__fund=fund)
            & models.Exists(History.objects.filter(author=models.OuterRef('pk')))),
            label_func=get_reviewer_label,
            label='Author', required=False)
        
        FormControlMixin.__init__(self)

        self.fields['author'].widget.attrs.update({
            'onchange': 'javascript:this.form.submit()'
        })
        
        self.order_fields(['date_range', 'name'])
        self.__resolvers__['author'] = lambda field: models.Q(author=field)
        self.__resolvers__['date_range'] = lambda field: models.Q(date_created__gte=field[0], date_created__lt=field[1])
 