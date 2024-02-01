import eav

from django.db import models
from commons.models import Base

from comments.models import Comment
from customfields.models import CustomFieldsEvaConfig
from files.models import Attachment
from funds.models import Fund


class ActiveWardManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_inactive=False)


class Ward(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    is_inactive = models.BooleanField()
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='wards')
    cover = models.ImageField(upload_to='covers', null=True)
    attachments = models.ManyToManyField(
        Attachment, related_name='ward_attachments')
    comments = models.ManyToManyField(Comment, related_name='commented_wards')

    objects = models.Manager()
    active_objects = ActiveWardManager()

    def __str__(self):
        return self.name


def fund_total_wards_count(self):
    return Ward.objects.filter(fund__id=self.id).aggregate(total=models.Count('id'))['total']


Fund.add_to_class('total_wards_count', property(
    fget=fund_total_wards_count))


eav.register(Ward, CustomFieldsEvaConfig)
