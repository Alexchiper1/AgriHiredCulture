from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CandidateSkillForm, JobForm, ApplicationForm, RegisterForm
from .models import CandidateSkill, Job, Application, UserProfile


def home(request):
    return render(request, "core/home.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data["role"]
            UserProfile.objects.create(user=user, role=role)
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "core/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


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