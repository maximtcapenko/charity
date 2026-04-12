from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder

from commons.models import Base


class History(Base):
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='histories')
    name = models.CharField(max_length=100, null=False)
    details = models.JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    url = models.URLField(null=True, blank=True)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    target_id = models.UUIDField()
    target = GenericForeignKey('target_content_type', 'target_id')

    class Meta:
        indexes = [
            models.Index(fields=['target_content_type', 'target_id']),
        ]
