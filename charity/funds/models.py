from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property

from commons.models import Base, Notification


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
    cover = models.ImageField(
        upload_to='covers', null=True)
    title = models.CharField(max_length=256, null=True, blank=True)
    mobile_phone = models.CharField(max_length=12, null=True, blank=True)


class Approvement(Base):
    author = models.ForeignKey(
        User, on_delete=models.PROTECT)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)
    is_rejected = models.BooleanField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['date_created']

    def __str__(self) -> str:
        return 'rejected' if self.is_rejected else 'approved'


class Contributor(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='contributors')
    notes = models.TextField(blank=True, null=True)
    is_company = models.BooleanField()
    mobile_phone = models.CharField(max_length=12, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    cover = models.ImageField(upload_to='covers', null=True)

    def __str__(self):
        return self.name


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

    @cached_property
    def available_amount(self):
        income_amount = self.incomes.aggregate(
            income_amount=models.Sum('amount', default=0))['income_amount']
        return self.amount - income_amount


class RequestReview(Base):
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='author_request_reviews')
    reviewer = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='reviewer_request_reviews')
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT)
    notes = models.TextField(blank=True, null=True)
    notification = models.ForeignKey(
        Notification, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['date_created']


def user_fund(self):
    return self.volunteer_profile.fund


def fund_total_volunteers_count(self):
    return VolunteerProfile.objects.filter(fund__id=self.id).aggregate(total=models.Count('id'))['total']


Fund.add_to_class('total_volunteers_count', property(
    fget=fund_total_volunteers_count))


fund_cached_property = cached_property(user_fund, name='fund')
User.add_to_class('fund', fund_cached_property)
fund_cached_property.__set_name__(User, 'fund')
