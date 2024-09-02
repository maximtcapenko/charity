from azure.identity import DefaultAzureCredential

from django.db import models
from django.db.models.fields.files import FieldFile
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.azure_storage import AzureStorage

from .storagers import StorageProvider


class FundAzureStorageFieldFile(FieldFile):
    def __init__(self, instance, field, name):
        super(FundAzureStorageFieldFile, self).__init__(
            instance, field, name
        )
        if instance.storage_provider == StorageProvider.LOCAL:
            self.storage = FileSystemStorage(
                location='%s/%s' % (settings.BASE_DIR, 'private'))
        else:
            azure_container = instance.fund.id.hex
            self.storage = AzureStorage(account_name=settings.STORAGE_ACCOUNT_NAME,
                                        azure_container=azure_container, token_credential=DefaultAzureCredential())


class CustomFileField(models.FileField):
    attr_class = FundAzureStorageFieldFile

    def pre_save(self, model_instance: models.Model, add: bool):
        model_instance.size = round(self.file.size / 1000)
        return super().pre_save(model_instance, add)
