from django.contrib import admin
from .models import UserProfile, CandidateProfile, Skill, CandidateSkill, EmployerProfile, Job, Application

admin.site.register(UserProfile)
admin.site.register(CandidateProfile)
admin.site.register(Skill)
admin.site.register(CandidateSkill)
admin.site.register(EmployerProfile)
admin.site.register(Job)
admin.site.register(Application)