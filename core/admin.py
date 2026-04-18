from django.contrib import admin
from .models import CandidateProfile, Skill, CandidateSkill

admin.site.register(CandidateProfile)
admin.site.register(Skill)
admin.site.register(CandidateSkill)