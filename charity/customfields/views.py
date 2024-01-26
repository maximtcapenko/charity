from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods

from commons.functions import user_should_be_volunteer


@user_passes_test(user_should_be_volunteer)
@require_http_methods(['GET'])
def get_fields_configuration(request):
    extendable_models = ['ward', 'project']
    types = ContentType.objects.filter(model__in=extendable_models).all()

    return render(request, 'fields_configuration.html', {
        'fund': request.user.volunteer_profile.fund,
        'types': types,
        'selected_type': request.GET.get('type_id')
    })
