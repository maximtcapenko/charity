from django.db import models
from django.contrib.contenttypes.models import ContentType

from commons.models import Base
from funds.models import Fund


class CustomField(Base):
    field_config = models.JSONField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)

"""
    public enum CustomFieldControlType
    {
        [Description("Checkbox")]
        CheckBox = 1,

        [Description("Text Field")]
        TextBox,

        [Description("Text Area")]
        TextArea,

        [Description("Select List")]
        SelectList,

        [Description("Datepicker")]
        DatePicker
    }
"""