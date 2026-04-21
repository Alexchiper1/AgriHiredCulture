from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden

from .forms import CandidateSkillForm, JobForm, ApplicationForm, RegisterForm
from .models import (
    CandidateSkill,
    Job,
    Application,
    UserProfile,
    CandidateProfile,
    EmployerProfile,
)


def get_user_role(user):
    if not user.is_authenticated:
        return ""

    try:
        return user.userprofile.role
    except UserProfile.DoesNotExist:
        return ""


def is_candidate(user):
    return get_user_role(user) == "candidate"


def is_employer(user):
    return get_user_role(user) == "employer"


def is_recruiter(user):
    return get_user_role(user) == "recruiter"


def home(request):
    return render(request, "core/home.html", {"user_role": get_user_role(request.user)})


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
            skill = form.cleaned_data["skill"]
            if CandidateSkill.objects.filter(candidate=candidate, skill=skill).exists():
                form.add_error("skill", "You already added this skill.")
            else:
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

    return render(
        request,
        "core/skill_list.html",
        {"skills": skills, "user_role": get_user_role(request.user)},
    )


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

    return render(request, "core/job_list.html", {"jobs": jobs, "user_role": get_user_role(request.user)})


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
def update_application_status(request, application_id):
    if request.method != "POST":
        return HttpResponseForbidden("Status updates must be submitted as a form.")

    application = get_object_or_404(Application.objects.select_related("job", "job__employer"), id=application_id)
    new_status = request.POST.get("status")

    if new_status not in {"Accepted", "Declined"}:
        return HttpResponseBadRequest("Invalid application status.")

    can_manage = False
    if is_employer(request.user):
        employer = get_object_or_404(EmployerProfile, user=request.user)
        can_manage = application.job.employer_id == employer.id
    elif is_recruiter(request.user) or request.user.is_superuser:
        can_manage = True

    if not can_manage:
        return HttpResponseForbidden("You cannot update this application.")

    application.status = new_status
    application.save()
    return redirect("application_list")


@login_required
def application_list(request):
    base_queryset = Application.objects.select_related(
        "candidate",
        "candidate__user",
        "job",
        "job__employer",
    ).prefetch_related("candidate__candidateskill_set__skill")

    if is_candidate(request.user):
        candidate = get_object_or_404(CandidateProfile, user=request.user)
        applications = base_queryset.filter(candidate=candidate)
    elif is_employer(request.user):
        employer = get_object_or_404(EmployerProfile, user=request.user)
        applications = base_queryset.filter(job__employer=employer)
    elif is_recruiter(request.user) or request.user.is_superuser:
        applications = base_queryset.all()
    else:
        applications = Application.objects.none()

    return render(
        request,
        "core/application_list.html",
        {"applications": applications, "user_role": get_user_role(request.user)},
    )