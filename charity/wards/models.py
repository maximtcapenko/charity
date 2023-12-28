from django.db import models
from files.models import Attachment
from funds.models import Fund

from commons.models import Base


class Ward(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='wards')
    cover = models.ForeignKey(Attachment, null=True,
                              on_delete=models.SET_NULL, related_name='wards')
    attachments = models.ManyToManyField(
        Attachment, related_name='ward_attachments')

    def __str__(self):
        return self.name

def fund_total_wards_count(self):
    return Ward.objects.filter(fund__id=self.id).aggregate(total=models.Count('id'))['total']


Fund.add_to_class('total_wards_count', property(
    fget=fund_total_wards_count))
