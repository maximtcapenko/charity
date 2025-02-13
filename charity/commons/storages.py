from azure.identity import DefaultAzureCredential

from storages.backends.azure_storage import AzureStorage

from django.conf import settings
from django.db import models


class StorageProvider(models.TextChoices):
    LOCAL = 'LOCAL', 'Local'
    AZURE = 'AZURE', 'Azure'


FILES = 'files'
THUMBS = 'thumbs'

SUFFIX_MAP = {
    FILES: 'private',
    THUMBS: 'public'
}


def storage_provider_resolver(container_name):
    return AzureStorage(account_name=settings.STORAGE_ACCOUNT_NAME,
                        azure_container=container_name,
                        token_credential=DefaultAzureCredential())


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
