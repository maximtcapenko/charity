from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob._blob_service_client import BlobServiceClient

from celery.backends.base import KeyValueStoreBackend
from celery.utils.log import get_logger

from django.conf import settings

from kombu.utils import cached_property
from kombu.utils.encoding import bytes_to_str


LOGGER = get_logger(__name__)


class CustomAzureBlockBlobBackend(KeyValueStoreBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        conf = self.app.conf

        self._credential = DefaultAzureCredential()
        self._connection_string = f"https://{settings.STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        self._container_name = 'django-celery'
        self._connection_timeout = conf.get(
            'azureblockblob_connection_timeout', 20
        )
        self.base_path = conf.get('azureblockblob_base_path', '')
        self._read_timeout = conf.get('azureblockblob_read_timeout', 120)

    @cached_property
    def _blob_service_client(self):
        client = BlobServiceClient(
            self._connection_string,
            self._credential,
            connection_timeout=self._connection_timeout,
            read_timeout=self._read_timeout
        )
        LOGGER.debug('Createing client')
        try:
            client.create_container(name=self._container_name)
            msg = f'Container created with name {self._container_name}.'
        except ResourceExistsError:
            msg = f'Container with name {self._container_name} already exists. This will not be created.'
        LOGGER.info(msg)

        return client

    def get(self, key):
        key = bytes_to_str(key)
        LOGGER.debug('Getting Azure Block Blob %s/%s',
                     self._container_name, key)

        blob_client = self._blob_service_client.get_blob_client(
            container=self._container_name,
            blob=f'{self.base_path}{key}',
        )

        try:
            return blob_client.download_blob().readall().decode()
        except ResourceNotFoundError:
            return None

    def set(self, key, value):
        key = bytes_to_str(key)
        LOGGER.debug(f'Creating azure blob at {self._container_name}/{key}')

        blob_client = self._blob_service_client.get_blob_client(
            container=self._container_name,
            blob=f'{self.base_path}{key}',
        )

        blob_client.upload_blob(value, overwrite=True)

    def mget(self, keys):
        return [self.get(key) for key in keys]

    def delete(self, key):
        key = bytes_to_str(key)
        LOGGER.debug(f'Deleting azure blob at {self._container_name}/{key}')

        blob_client = self._blob_service_client.get_blob_client(
            container=self._container_name,
            blob=f'{self.base_path}{key}',
        )

        blob_client.delete_blob()
