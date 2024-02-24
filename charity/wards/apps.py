from django.apps import AppConfig


class WardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wards'

    def ready(self):
        from .signals import when_task_has_been_completed_linked_attribute_should_be_set
        return super().ready()
