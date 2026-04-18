from django.shortcuts import render, redirect
from .forms import CandidateSkillForm
from .models import CandidateSkill


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