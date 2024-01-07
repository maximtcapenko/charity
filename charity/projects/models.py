from django.db import models
from django.contrib.auth.models import User
from commons.models import Base
from funds.models import Fund
from processes.models import Process
from wards.models import Ward


class Project(Base):
    name = models.CharField(max_length=256, blank=False,
                            unique=True, null=False)
    notes = models.TextField(blank=True, null=True)
    fund = models.ForeignKey(
        Fund, on_delete=models.PROTECT, related_name='projects')
    cover = models.ImageField(upload_to='covers', null=True)
    wards = models.ManyToManyField(Ward, related_name='projects')
    processes = models.ManyToManyField(Process, related_name='projects')
    leader = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='leaded_projects')
    closed_date = models.DateField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)


def fund_projects_count(self):
    return Project.objects.filter(fund__id=self.id).aggregate(
        total=models.Count('id'))['total']


def fund_active_projects_count(self):
    return Project.objects.filter(fund__id=self.id, is_closed=False).aggregate(
        total=models.Count('id'))['total']


def fund_active_projects(self):
    return Project.objects.filter(fund__id=self.id, is_closed=False)\
        .select_related('leader') \
        .all()


def ward_active_projects(self):
    return self.projects.filter(is_closed=False).all()


Fund.add_to_class('projects_count', property(
    fget=fund_projects_count))

Fund.add_to_class('active_projects_count', property(
    fget=fund_active_projects_count))

Fund.add_to_class('active_projects', property(
    fget=fund_active_projects))

Ward.add_to_class('active_projects', property(
    fget=ward_active_projects
))
