from commons.models import Base
from django.db import models
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
    is_first = models.BooleanField(default=False)
    is_inactive = models.BooleanField(default=False)
    next_state = models.ForeignKey('self', null=True, on_delete=models.PROTECT)


    def __str__(self):
        return self.name
