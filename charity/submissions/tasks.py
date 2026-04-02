import datetime
import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from django.core.files.base import ContentFile
from django.template import Template, Context, loader
from django.utils.safestring import mark_safe
from django.utils.crypto import get_random_string

from submissions.models import SubmissionLog, SubmissionSentStatus

logger = logging.getLogger(__name__)

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


from celery import shared_task
import datetime

@shared_task(bind=True, max_retries=5, default_retry_delay=5)
def send_submssions(self, submission_log_id):
    submissionLog = None

    try:
        submissionLog = SubmissionLog.objects.get(pk=submission_log_id)
    except SubmissionLog.DoesNotExist:
        logger.error(f'SubmissionLog {submission_log_id} not found')
        return
    except Exception as exc:
        logger.exception(exc)
        raise self.retry(exc=exc)

    try:
        submissionLog.status = SubmissionSentStatus.IN_PROGRESS
        submissionLog.save()

        submission = submissionLog.submission
        fund = submissionLog.fund
        partitions = list()
    
        usesrTemplate = Template(submission.mailing_template.template)
        layoutTemplte = loader.get_template('emails/example_email.html')
        
        for ward in submission.wards.all():
            context = Context(WrappedContext(ward))
            partitions.append(mark_safe(usesrTemplate.render(context)))

        result = layoutTemplte.render({
            'blocks': partitions,
            'document_name': 'New Wards info',
            'fund': fund,
            'date_generated': datetime.datetime.now(datetime.timezone.utc)
        })

        name = f'{get_random_string(10)}.html'
        submissionLog.file.save(name, ContentFile(result.encode(), name))

        submissionLog.status = SubmissionSentStatus.SENT
        submissionLog.is_delivered = True
        submissionLog.delivery_date = datetime.datetime.now(datetime.timezone.utc)
        submissionLog.save()

    except Exception as exc:
        logger.exception(exc)

        try:
            submissionLog.retries_count = self.request.retries
            submissionLog.save(update_fields=['retries_count'])
        except Exception:
            logger.exception('Failed to update retries_count')

        if self.request.retries >= self.max_retries:
            submissionLog.status = SubmissionSentStatus.FAILED
            submissionLog.error_date = datetime.datetime.now(datetime.timezone.utc)
            submissionLog.retries_count = self.request.retries
            submissionLog.error_message = f'{type(exc).__name__}: {exc}'
            submissionLog.is_delivered = False
            submissionLog.save()
            return

        raise self.retry(exc=exc)
