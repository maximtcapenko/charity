from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET

from commons import DEFAULT_PAGE_SIZE
from commons.functional import user_should_be_volunteer

from .forms import SearchHistoryForm
from .models import History


@user_passes_test(user_should_be_volunteer)
@require_GET
def get_list(request):
    search_form = SearchHistoryForm(request.user.fund, request.GET)
    paginator = Paginator(search_form.get_search_queryset(History.objects.all()), DEFAULT_PAGE_SIZE)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'history_list.html', {
        'title': 'History',
        'page': page,
        'search_form': search_form,
        'items_count': paginator.count
    })
