from django.contrib import admin
from .models import Fund, Contribution, Approvement

admin.site.register(Fund)
admin.site.register(Contribution)
admin.site.register(Approvement)
