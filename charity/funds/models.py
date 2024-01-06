from django.db import models
from django.contrib.auth.models import User
from commons.models import Base


class Fund(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    cover = models.ImageField(upload_to='covers', null=True)

    def __str__(self):
        return self.name


class VolunteerProfile(Base):
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='volunteers')
    user = models.OneToOneField(
        User, related_name='volunteer_profile', on_delete=models.PROTECT)
    cover = models.ImageField(upload_to='covers', null=True)
    title = models.CharField(max_length=256, null=True, blank=True)
    mobile_phone = models.CharField(max_length=12, null=True, blank=True)


class Approvement(Base):
    author = models.ForeignKey(
        User, on_delete=models.PROTECT)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)
    is_rejected = models.BooleanField()
    notes = models.TextField(blank=True, null=True)


class Contributor(Base):
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='contributors')
    notes = models.TextField(blank=True, null=True)
    is_company = models.BooleanField()


class Contribution(Base):
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='contributions')
    contribution_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT)
    contributor = models.ForeignKey(
        Contributor, on_delete=models.PROTECT, related_name='contributions')


def fund_total_contributors_count(self):
    return Contributor.objects.filter(fund__id=self.id).aggregate(total=models.Count('id'))['total']


def fund_total_volunteers_count(self):
    return VolunteerProfile.objects.filter(fund__id=self.id).aggregate(total=models.Count('id'))['total']


Fund.add_to_class('total_volunteers_count', property(
    fget=fund_total_volunteers_count))

Fund.add_to_class('total_contributors_count', property(
    fget=fund_total_contributors_count))
