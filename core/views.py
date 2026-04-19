from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .forms import CandidateSkillForm, JobForm, ApplicationForm, RegisterForm
from .models import (
    CandidateSkill,
    Job,
    Application,
    UserProfile,
    CandidateProfile,
    EmployerProfile,
)


def is_candidate(user):
    return hasattr(user, "userprofile") and user.userprofile.role == "candidate"


def is_employer(user):
    return hasattr(user, "userprofile") and user.userprofile.role == "employer"


def is_recruiter(user):
    return hasattr(user, "userprofile") and user.userprofile.role == "recruiter"


def home(request):
    return render(request, "core/home.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data["role"]
            UserProfile.objects.create(user=user, role=role)

            if role == "candidate":
                CandidateProfile.objects.create(
                    user=user,
                    full_name=user.username,
                    location="",
                    bio=""
                )
            elif role == "employer":
                EmployerProfile.objects.create(
                    user=user,
                    company_name=user.username,
                    location=""
                )

            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "core/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def add_candidate_skill(request):
    if not is_candidate(request.user):
        return HttpResponseForbidden("Only candidates can add skills.")

    candidate = get_object_or_404(CandidateProfile, user=request.user)

    if request.method == "POST":
        form = CandidateSkillForm(request.POST)
        if form.is_valid():
            candidate_skill = form.save(commit=False)
            candidate_skill.candidate = candidate
            candidate_skill.save()
            return redirect("skill_list")
    else:
        form = CandidateSkillForm()

    return render(request, "core/add_candidate_skill.html", {"form": form})


@login_required
def skill_list(request):
    if is_candidate(request.user):
        candidate = get_object_or_404(CandidateProfile, user=request.user)
        skills = CandidateSkill.objects.select_related("candidate", "skill").filter(candidate=candidate)
    else:
        skills = CandidateSkill.objects.select_related("candidate", "skill").all()

    return render(request, "core/skill_list.html", {"skills": skills})


@login_required
def add_job(request):
    if not is_employer(request.user):
        return HttpResponseForbidden("Only employers can add jobs.")

    employer = get_object_or_404(EmployerProfile, user=request.user)

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = employer
            job.save()
            return redirect("job_list")
    else:
        form = JobForm()

    return render(request, "core/add_job.html", {"form": form})


@login_required
def job_list(request):
    if is_employer(request.user):
        employer = get_object_or_404(EmployerProfile, user=request.user)
        jobs = Job.objects.select_related("employer").filter(employer=employer)
    else:
        jobs = Job.objects.select_related("employer").all()

    return render(request, "core/job_list.html", {"jobs": jobs})


@login_required
def add_application(request, job_id):
    if not is_candidate(request.user):
        return HttpResponseForbidden("Only candidates can apply for jobs.")

    candidate = get_object_or_404(CandidateProfile, user=request.user)
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            if not Application.objects.filter(candidate=candidate, job=job).exists():
                application = form.save(commit=False)
                application.candidate = candidate
                application.job = job
                application.status = "Pending"
                application.save()
            return redirect("application_list")
    else:
        form = ApplicationForm()

    return render(request, "core/add_application.html", {"form": form, "job": job})


@login_required
def application_list(request):
    if is_candidate(request.user):
        candidate = get_object_or_404(CandidateProfile, user=request.user)
        applications = Application.objects.select_related("candidate", "job").filter(candidate=candidate)
    elif is_employer(request.user):
        employer = get_object_or_404(EmployerProfile, user=request.user)
        applications = Application.objects.select_related("candidate", "job", "job__employer").filter(job__employer=employer)
    elif is_recruiter(request.user) or request.user.is_superuser:
        applications = Application.objects.select_related("candidate", "job").all()
    else:
        applications = Application.objects.none()

    return render(request, "core/application_list.html", {"applications": applications})