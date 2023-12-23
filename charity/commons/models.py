import uuid
from django.db import models


class Base(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    date_created = models.DateTimeField(auto_now_add=True, null=False)
