from django.shortcuts import render
from .models import Process


def get_list(request):
    return render(request, 'processes_list.html', {
        'processes': Process.objects.all()
    })
