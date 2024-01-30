import eav

from django.db import models
from django.contrib.contenttypes.models import ContentType

from eav.registry import EavConfig
from eav.models import Attribute

from commons.models import Base
from funds.models import Fund


class CustomField(Base):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)
    attribute = models.OneToOneField(
        Attribute, on_delete=models.CASCADE, related_name='custom_field')
    is_public = models.BooleanField(default=False, null=False)


class CustomFieldsEvaConfig(EavConfig):
    eav_attr = 'custom_fields'
    
    @classmethod
    def get_attributes(cls, instance=None):
        return Attribute.objects.select_related('custom_field').all()
