from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404

from commons.functions import user_should_be_volunteer
from .models import Attachment


@login_required
@user_passes_test(user_should_be_volunteer)
def get_file(request, id):
    file = get_object_or_404(Attachment, pk=id)
    return FileResponse(file.file)
