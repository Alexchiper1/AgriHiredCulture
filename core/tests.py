from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import UserProfile, CandidateProfile, Skill, CandidateSkill, EmployerProfile, Job, Application


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="candidate1", password="password")
        self.profile = UserProfile.objects.create(user=self.user, role="candidate")
        self.candidate = CandidateProfile.objects.create(
            user=self.user,
            full_name="Candidate One",
            location="Carlow",
            bio="Experienced farm worker"
        )
        self.skill = Skill.objects.create(name="Tractor Driving")

    def test_skill_creation(self):
        self.assertEqual(self.skill.name, "Tractor Driving")

    def test_candidate_profile_creation(self):
        self.assertEqual(self.candidate.full_name, "Candidate One")

    def test_candidate_skill_creation(self):
        candidate_skill = CandidateSkill.objects.create(candidate=self.candidate, skill=self.skill)
        self.assertEqual(candidate_skill.candidate.full_name, "Candidate One")
        self.assertEqual(candidate_skill.skill.name, "Tractor Driving")


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AgriHiredCulture")

    def test_register_page_loads(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)


class IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.candidate_user = User.objects.create_user(username="candidate2", password="password")
        self.candidate_role = UserProfile.objects.create(user=self.candidate_user, role="candidate")
        self.candidate = CandidateProfile.objects.create(
            user=self.candidate_user,
            full_name="Candidate Two",
            location="Kilkenny",
            bio="Harvest specialist"
        )

        self.employer_user = User.objects.create_user(username="employer1", password="password")
        self.employer_role = UserProfile.objects.create(user=self.employer_user, role="employer")
        self.employer = EmployerProfile.objects.create(
            user=self.employer_user,
            company_name="Green Farm Ltd",
            location="Wexford"
        )

        self.skill = Skill.objects.create(name="Irrigation")
        self.job = Job.objects.create(
            employer=self.employer,
            title="Farm Assistant",
            description="Help with crops and irrigation",
            location="Wexford"
        )

    def test_candidate_can_be_given_skill(self):
        candidate_skill = CandidateSkill.objects.create(candidate=self.candidate, skill=self.skill)
        self.assertEqual(candidate_skill.skill.name, "Irrigation")

    def test_job_creation(self):
        self.assertEqual(self.job.title, "Farm Assistant")
        self.assertEqual(self.job.employer.company_name, "Green Farm Ltd")

    def test_application_creation(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status="Pending"
        )
        self.assertEqual(application.job.title, "Farm Assistant")
        self.assertEqual(application.candidate.full_name, "Candidate Two")


class UseCaseTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.candidate_user = User.objects.create_user(username="user1", password="password")
        UserProfile.objects.create(user=self.candidate_user, role="candidate")
        self.candidate = CandidateProfile.objects.create(
            user=self.candidate_user,
            full_name="User One",
            location="Dublin",
            bio="General farm worker"
        )

        self.employer_user = User.objects.create_user(username="adminfarm", password="password")
        UserProfile.objects.create(user=self.employer_user, role="employer")
        self.employer = EmployerProfile.objects.create(
            user=self.employer_user,
            company_name="Agri Jobs Co",
            location="Cork"
        )

        self.skill = Skill.objects.create(name="Livestock Handling")
        self.job = Job.objects.create(
            employer=self.employer,
            title="Livestock Assistant",
            description="Assist with livestock care",
            location="Cork"
        )

    def test_full_candidate_to_application_flow(self):
        candidate_skill = CandidateSkill.objects.create(candidate=self.candidate, skill=self.skill)
        application = Application.objects.create(candidate=self.candidate, job=self.job, status="Pending")

        self.assertEqual(candidate_skill.skill.name, "Livestock Handling")
        self.assertEqual(application.candidate.full_name, "User One")
        self.assertEqual(application.job.title, "Livestock Assistant")
        self.assertEqual(application.status, "Pending")