from django.contrib.auth.models import User
from django.db import models

from commons import storages
from commons.fields import FundFileField
from commons.models import Base
from funds.models import Fund
from mailings.models import MailingGroup, MailingTemplate
from wards.models import Ward


class SubmissionSentStatus(models.TextChoices):
    QUEUED = 'QUEUED', 'In queue'
    SENT = 'SENT', 'Sent'
    IN_PROGRESS = 'IN_PROGRESS', 'In progress'
    PARTIALLY_SENT = 'PARTIALLY_SENT', 'Partially sent'
    FAILED = 'FAILED', 'Failed'


class Submission(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    is_draft = models.BooleanField(default=True, null=False)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)
    wards = models.ManyToManyField(Ward)
    mailing_template = models.ForeignKey(
        MailingTemplate, on_delete=models.PROTECT, related_name='submissions')
    mailing_group = models.ForeignKey(MailingGroup, on_delete=models.PROTECT, related_name='submissions')
    is_draft = models.BooleanField()
    last_update_date = models.DateTimeField(auto_now=True, null=True)

class SubmissionLog(Base):
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name='logs')
    session_id = models.UUIDField(null=False)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE) 
    recipient_email = models.CharField(max_length=256, blank=False, null=False)
    recipient_name = models.CharField(max_length=1000, blank=True, null=True)
    subject = models.CharField(max_length=1000, blank=False, null=True, )
    file = FundFileField(null=True, upload_to=storages.EMAILS)
    status = models.CharField(
        choices=SubmissionSentStatus.choices, max_length=16)
    retries_count = models.IntegerField(default=0)
    is_delivered = models.BooleanField(null=True)
    delivery_date = models.DateTimeField(null=True)
    error_message = models.CharField(max_length=1000, null=True, blank=True)
    error_date = models.DateTimeField(null=True)

