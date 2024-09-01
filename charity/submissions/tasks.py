from celery import shared_task

from django.utils.safestring import mark_safe
from django.template import Template, Context, loader
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile

from commons import storagers

from .models import Submission, SubmissionSentStatus


class WrappedContext:
    def __init__(self, ward):
        self.ward = ward
        self._own_keys = set(self.ward.__dict__.keys())
        self._custom_keys = self.ward.custom_fields.get_all_attribute_slugs()
        self.keys = self._own_keys.union(self._custom_keys)

    def __contains__(self, key):
        return key in self.keys

    def __getitem__(self, key):
        if key in self._own_keys:
            return self.ward.__dict__[key]

        if key in self._custom_keys:
            attr = self.ward.custom_fields.get_attribute_by_slug(key)
            return self.ward.custom_fields.get_value_by_attribute(attr).value

        return None


@shared_task
def send_submssions(submission_id):
    submission = Submission.objects.get(pk=submission_id)
    submission.is_draft = False
    submission.status = SubmissionSentStatus.IN_PROGRESS
    submission.save()

    partitions = list()
    template = Template(submission.mailing_template.template)

    layout = loader.get_template('partials/submission_item_layout.html')

    for ward in submission.wards.all():
        context = Context(WrappedContext(ward))
        partitions.append(mark_safe(f'<div>{template.render(context)}</div>'))

    result = layout.render({
        'blocks': partitions
    })

    name = f'emails/{get_random_string(10)}.html'
    storagers.private.save(name, ContentFile(result.encode(), name))
    submission.status = SubmissionSentStatus.SENT
    submission.save()
