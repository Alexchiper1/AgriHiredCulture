from django.shortcuts import render, redirect
from .forms import CandidateSkillForm, JobForm, ApplicationForm
from .models import CandidateSkill, Job, Application


def home(request):
    return render(request, "core/home.html")


def add_candidate_skill(request):
    if request.method == "POST":
        form = CandidateSkillForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("skill_list")
    else:
        form = CandidateSkillForm()

    return render(request, "core/add_candidate_skill.html", {"form": form})


def skill_list(request):
    skills = CandidateSkill.objects.select_related("candidate", "skill").all()
    return render(request, "core/skill_list.html", {"skills": skills})


def add_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("job_list")
    else:
        form = JobForm()

    return render(request, "core/add_job.html", {"form": form})


def job_list(request):
    jobs = Job.objects.select_related("employer").all()
    return render(request, "core/job_list.html", {"jobs": jobs})


def add_application(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("application_list")
    else:
        form = ApplicationForm()

    return render(request, "core/add_application.html", {"form": form})


def application_list(request):
    applications = Application.objects.select_related("candidate", "job").all()
    return render(request, "core/application_list.html", {"applications": applications})