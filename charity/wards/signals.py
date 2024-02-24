from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from customfields.models import CustomField, Attribute
from tasks.models import Task
from tasks.signals import task_has_been_completed

from .models import Ward

VALID_FIELD_VALUES = {
    Attribute.TYPE_BOOLEAN: True,
    Attribute.TYPE_TEXT: 'Yes'
}


@receiver(task_has_been_completed, sender=Task)
def when_task_has_been_completed_linked_attribute_should_be_set(sender, instance, **kwagrs):
    content_type = ContentType.objects.get_for_model(model=Ward)
    field = CustomField.objects.filter(
        linked_process=instance.process, content_type=content_type).first()
    if field:
        value = VALID_FIELD_VALUES.get(field.attribute.datatype)
        if value:
            setattr(instance.ward.custom_fields, field.attribute.slug, value)
            instance.ward.custom_fields.save()
