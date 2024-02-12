from django.contrib.auth.models import User
from django.db import models

from commons.models import Base
from funds.models import Fund
from mailings.models import MailingGroup, MailingTemplate
from wards.models import Ward


class SubmissionSentStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Is draft'
    SENT = 'SENT', 'Sent'
    IN_PROGRESS = 'IN_PROGRESS', 'In progress'
    PARTIALLY_SENT = 'PARTIALLY_SENT', 'Partially sent'


class Submission(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    is_draft = models.BooleanField(default=True, null=False)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)
    wards = models.ManyToManyField(Ward)
    mailing_template = models.ForeignKey(
        MailingTemplate, on_delete=models.PROTECT)
    mailing_group = models.ForeignKey(MailingGroup, on_delete=models.PROTECT)
    status = models.CharField(
        choices=SubmissionSentStatus.choices, max_length=16)
