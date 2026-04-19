from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    UserProfile,
    CandidateProfile,
    EmployerProfile,
    Skill,
    CandidateSkill,
    Job,
    Application,
)


class Command(BaseCommand):
    help = "Seed the database with initial fixture data"

    def handle(self, *args, **kwargs):
        # Clear existing data
        Application.objects.all().delete()
        CandidateSkill.objects.all().delete()
        Job.objects.all().delete()
        Skill.objects.all().delete()
        CandidateProfile.objects.all().delete()
        EmployerProfile.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # Admin
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@admin.com", "is_staff": True, "is_superuser": True}
        )
        admin_user.set_password("password")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # Candidate user1
        user1 = User.objects.create_user(
            username="user1",
            email="user1@user1.com",
            password="password"
        )
        UserProfile.objects.create(user=user1, role="candidate")
        candidate1 = CandidateProfile.objects.create(
            user=user1,
            full_name="User One",
            location="Carlow",
            bio="Experienced agricultural worker"
        )

        # Candidate user2
        user2 = User.objects.create_user(
            username="user2",
            email="user2@user2.com",
            password="password"
        )
        UserProfile.objects.create(user=user2, role="candidate")
        candidate2 = CandidateProfile.objects.create(
            user=user2,
            full_name="User Two",
            location="Kilkenny",
            bio="Skilled in harvesting and irrigation"
        )

        # Employer
        employer_user = User.objects.create_user(
            username="farmboss",
            email="farmboss@farm.com",
            password="password"
        )
        UserProfile.objects.create(user=employer_user, role="employer")
        employer = EmployerProfile.objects.create(
            user=employer_user,
            company_name="Green Fields Farm",
            location="Wexford"
        )

        # Recruiter
        recruiter_user = User.objects.create_user(
            username="recruiter1",
            email="recruiter1@agri.com",
            password="password"
        )
        UserProfile.objects.create(user=recruiter_user, role="recruiter")

        # Skills
        tractor = Skill.objects.create(name="Tractor Driving")
        irrigation = Skill.objects.create(name="Irrigation")
        harvesting = Skill.objects.create(name="Harvesting")
        livestock = Skill.objects.create(name="Livestock Handling")

        # Candidate skills
        CandidateSkill.objects.create(candidate=candidate1, skill=tractor)
        CandidateSkill.objects.create(candidate=candidate1, skill=livestock)
        CandidateSkill.objects.create(candidate=candidate2, skill=irrigation)
        CandidateSkill.objects.create(candidate=candidate2, skill=harvesting)

        # Jobs
        job1 = Job.objects.create(
            employer=employer,
            title="Farm Assistant",
            description="Assist with livestock and daily farm operations",
            location="Wexford"
        )

        job2 = Job.objects.create(
            employer=employer,
            title="Irrigation Worker",
            description="Support irrigation and crop maintenance",
            location="Wexford"
        )

        # Applications
        Application.objects.create(candidate=candidate1, job=job1, status="Pending")
        Application.objects.create(candidate=candidate2, job=job2, status="Pending")

        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))