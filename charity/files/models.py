import uuid

from io import BytesIO

from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models

from PIL import Image

from commons import storages
from commons.models import Base
from commons.fields import FundFileField
from funds.models import Fund


class Attachment(Base):
    class AttachmentType(models.TextChoices):
        IMG = 'IMG', 'Image'
        PDF = 'PDF', 'Pdf'
        DOC = 'DOC', 'Word'
        EXCEL = 'EXCEL', 'Excel'
        VIDEO = 'VIDEO', 'Video'

    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    file = FundFileField(upload_to=storages.FILES)
    thumb = FundFileField(upload_to=storages.THUMBS)
    type = models.CharField(choices=AttachmentType.choices, max_length=6)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)
    storage_provider = models.CharField(
        max_length=10, default=settings.DEFAULT_STORAGE_PROVIDER)
    is_public = models.BooleanField(default=False)
    size = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.file:
            self._create_thumbnail()

        super().save(*args, **kwargs)

    def _create_thumbnail(self):      
        if self.file.file.content_type in ('image/jpeg'):
            img = Image.open(self.file)
            img.thumbnail((50, 50))
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG')
            thumb_filename = f'thumb_{uuid.uuid1().hex}.jpeg'
            self.thumb.save(thumb_filename, ContentFile(
            thumb_io.getvalue()), save=False)
        else:
            pass
