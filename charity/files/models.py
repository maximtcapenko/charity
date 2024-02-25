from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property

from commons.models import Base
from commons import storagers
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
    file = models.FileField(upload_to='files', storage=storagers.private)
    type = models.CharField(choices=AttachmentType.choices, max_length=6)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)

    @cached_property
    def size(self):
        return round(self.file.size / 1000)

    def __str__(self):
        return f'{self.name} ({self.type})'
