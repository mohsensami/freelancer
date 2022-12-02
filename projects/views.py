from django.shortcuts import render, redirect, get_object_or_404
from .models import Project
from django.views import View
from .forms import ProjectForm, ReviewForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .utils import searchProjects, paginateProjects


def projects(request):
    projects, search_query = searchProjects(request)
    custom_range, projects = paginateProjects(request, projects, 6)

    context = {'projects': projects, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'projects/projects.html', context)


def project(request, pk):
    projectObj = Project.objects.get(id=pk)
    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        review = form.save(commit=False)
        review.project = projectObj
        review.owner = request.user.profile
        review.save()

        projectObj.getVoteCount

        messages.success(request, 'Your review was successfully submitted!')
        return redirect('project', pk=projectObj.id)
    return render(request, 'projects/single_project.html', {'project': projectObj, 'form': form})


class CreateProject(LoginRequiredMixin, View):
    form_class = ProjectForm

    def get(self, request):
        form = self.form_class()
        return render(request, 'projects/project_form.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        profile = request.user.profile
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            project = form.save()
            return redirect('projects')


class UpdateProject(LoginRequiredMixin, View):
    form_class = ProjectForm

    def setup(self, request, *args, **kwargs):
        self.project_instance = get_object_or_404(Project, pk = kwargs['pk'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, pk):
        project = self.project_instance
        form = self.form_class(instance=project)
        return render(request, 'projects/project_form.html', {'form': form})

    def post(self, request, pk):
        project = self.project_instance
        form = self.form_class(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects')


class DeleteProject(View):
    form_class = ProjectForm

    def setup(self, request, *args, **kwargs):
        self.project_instance = get_object_or_404(Project, pk = kwargs['pk'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, pk):
        obj = self.project_instance
        return render(request, 'projects/delete_template.html', {'obj': obj})

    def post(self, request, pk):
        project = self.project_instance
        project.delete()
        return redirect('projects')