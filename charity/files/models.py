from django.db import models

from commons.models import Base


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
    path = models.FilePathField()
    type = models.CharField(choices=AttachmentType.choices, max_length=6)
