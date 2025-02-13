from typing import Any
from django.db import models
from django.db.models.fields.files import FieldFile

from .storages import storage_provider_resolver, SUFFIX_MAP, FILES


class FundStorageFieldFile(FieldFile):
    """
    This object depend on `storage_provider` attribute of `model_instance`
    """

    def __init__(self, instance, field, name):
        super(FundStorageFieldFile, self).__init__(
            instance, field, name
        )

        suffix = SUFFIX_MAP.get(field.upload_to, FILES)
        storage = storage_provider_resolver(f'{instance.fund.id.hex}-{suffix}')
        self.storage = storage


class FundFileField(models.FileField):
    """
    This field will be used instance of Fund class in oorder to resolve
    location of files
    """
    attr_class = FundStorageFieldFile

    def pre_save(self, model_instance: models.Model, add: bool):
        file = super().pre_save(model_instance, add)
        model_instance.size = round(file.size / 1000)
        return file
