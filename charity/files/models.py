from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property

from commons.models import Base
from commons.fields import CustomFileField, StorageProvider
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
    file = CustomFileField(upload_to='files')
    type = models.CharField(choices=AttachmentType.choices, max_length=6)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)
    storage_provider = models.CharField(
        choices=StorageProvider.choices, max_length=10, default=StorageProvider.AZURE)
    size = models.IntegerField()

    def __str__(self):
        return f'{self.name} ({self.type})'
