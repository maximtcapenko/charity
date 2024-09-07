from azure.identity import DefaultAzureCredential

from storages.backends.azure_storage import AzureStorage

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models


class StorageProvider(models.TextChoices):
    LOCAL = 'LOCAL', 'Local'
    AZURE = 'AZURE', 'Azure'


storages = {
    StorageProvider.AZURE: lambda fund: AzureStorage(account_name=settings.STORAGE_ACCOUNT_NAME,
                                                     azure_container=fund.id.hex, token_credential=DefaultAzureCredential()),
    StorageProvider.LOCAL: lambda fund: FileSystemStorage(
        location='%s/%s/%s' % (settings.BASE_DIR, 'private', fund.id.hex))
}


def storage_provider_resolver(type):
    """
    Returns function `func(fund: Fund) -> Storage`
    """
    storage = storages.get(type)
    if not storages:
        raise NotImplementedError(
            f'Storage with type {type} is not implemented')

    return storage


class AzureStaticStorage(AzureStorage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.account_name = settings.STORAGE_ACCOUNT_NAME
        self.token_credential = DefaultAzureCredential()
        self.azure_container = 'static'

class AzureMediaStorage(AzureStorage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.account_name = settings.STORAGE_ACCOUNT_NAME
        self.token_credential = DefaultAzureCredential()
        self.azure_container = 'media'