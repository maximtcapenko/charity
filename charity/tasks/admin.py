from django.contrib import admin
from .models import Task, TaskState, Comment, Expense

admin.site.register(Task)
admin.site.register(TaskState)
admin.site.register(Comment)
admin.site.register(Expense)
