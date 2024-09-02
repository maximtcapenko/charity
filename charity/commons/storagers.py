from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models

class StorageProvider(models.TextChoices):
    LOCAL = 'LOCAL', 'Local'
    AZURE = 'AZURE', 'Azure'


private = FileSystemStorage(location= '%s/%s' % (settings.BASE_DIR, 'private'))