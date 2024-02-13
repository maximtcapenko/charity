from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from commons.models import Base
from budgets.models import Fund
from funds.models import Contributor


class MailingGroup(Base):
    name = models.CharField(max_length=256)
    notes = models.TextField(blank=True, null=True)
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='mailing_groups')
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='mailing_groups')
    recipients = models.ManyToManyField(Contributor)

    def __str__(self):
        return self.name


class MailingTemplate(Base):
    name = models.CharField(max_length=256)
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='templates')
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='email_templates')
    template = models.TextField(blank=False, null=False)
    subject = models.CharField(max_length=256)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
