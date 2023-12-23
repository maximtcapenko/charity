import uuid
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from commons.functions import user_should_be_volunteer
from .forms import ProjectForm
from .models import Project


@login_required
@user_passes_test(user_should_be_volunteer)
def create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save()
            return redirect(reverse('funds:fund_details', args=[str(project.fund_id)]))
        else:
            return render(request, 'project_create.html', {
                'form': form
            })
    elif request.method == 'GET':
        fund_id = request.user.volunteer_profile.fund_id
        if fund_id is None:
            pass

        if isinstance(fund_id, uuid.UUID) is False:
            print('Error')

        return render(request, 'project_create.html', {
            'form': ProjectForm(initial={
                'fund': request.user.volunteer_profile.fund
            })
        })
    else:
        return render(request, "405.html", status=405)


@login_required
@user_passes_test(user_should_be_volunteer)
def get_list(request):
    projects = Project.objects.filter(
        fund_id=request.user.volunteer_profile.fund_id).all()
    
    return render(request, 'projects_list.html', {
        'projects': projects
    })


@login_required
@user_passes_test(user_should_be_volunteer)
def get_details(request, id):
    project = get_object_or_404(Project.objects.filter(\
        fund_id=request.user.volunteer_profile.fund_id), pk=id)
    paginator = Paginator(project.tasks.select_related('expense', 'expense__approvement').order_by(
        'order_position'), per_page=10)

    return render(request, 'project_details.html', {
        'project': project,
        'tasks_page': paginator.get_page(request.GET.get('page'))
    })
