from django.db import models

from commons.models import Base
from funds.models import Fund


class Process(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='processes')
    is_inactive = models.BooleanField()

    def __str__(self):
        return self.name


class ProcessState(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    process = models.ForeignKey(
        Process, on_delete=models.PROTECT, related_name='states')
    order_position = models.IntegerField()
    is_approvement_required = models.BooleanField(
        default=False, verbose_name='Require approvement')
    is_inactive = models.BooleanField(default=False)

    class Meta:
        ordering = ['order_position']

    def __str__(self):
        return self.name
