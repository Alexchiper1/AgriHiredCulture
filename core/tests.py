from django.core.management import call_command
from django.contrib.auth.models import User
from django.test import Client, TestCase

from .models import (
    Application,
    CandidateProfile,
    CandidateSkill,
    EmployerProfile,
    Job,
    Skill,
    UserProfile,
)


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


class ViewAndRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AgriHiredCulture")

    def test_logged_out_homepage_shows_only_auth_actions(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/register/"')
        self.assertContains(response, 'href="/login/"')
        self.assertNotContains(response, 'href="/jobs/" class="btn btn-light btn-sm"')
        self.assertNotContains(response, 'href="/skills/" class="btn btn-light btn-sm"')
        self.assertNotContains(response, 'href="/applications/" class="btn btn-light btn-sm"')
        self.assertContains(response, "Login to Access", count=3)

    def test_register_page_loads(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_candidate_registration_creates_role_and_profile(self):
        response = self.client.post(
            "/register/",
            {
                "username": "newcandidate",
                "email": "newcandidate@example.com",
                "role": "candidate",
                "password1": "Testpass123!",
                "password2": "Testpass123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="newcandidate")
        self.assertEqual(user.userprofile.role, "candidate")
        self.assertTrue(CandidateProfile.objects.filter(user=user).exists())

    def test_employer_registration_creates_role_and_profile(self):
        response = self.client.post(
            "/register/",
            {
                "username": "newemployer",
                "email": "newemployer@example.com",
                "role": "employer",
                "password1": "Testpass123!",
                "password2": "Testpass123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="newemployer")
        self.assertEqual(user.userprofile.role, "employer")
        self.assertTrue(EmployerProfile.objects.filter(user=user).exists())

    def test_recruiter_registration_creates_role(self):
        response = self.client.post(
            "/register/",
            {
                "username": "newrecruiter",
                "email": "newrecruiter@example.com",
                "role": "recruiter",
                "password1": "Testpass123!",
                "password2": "Testpass123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="newrecruiter")
        self.assertEqual(user.userprofile.role, "recruiter")

    def test_homepage_loads_for_superuser_without_userprofile(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@admin.com",
            password="password",
        )
        self.client.login(username="admin", password="password")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, admin_user.username)


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


class SeedDataTests(TestCase):
    def test_seed_data_command_populates_database(self):
        call_command("seed_data", verbosity=0)
        self.assertEqual(User.objects.count(), 5)
        self.assertEqual(UserProfile.objects.count(), 4)
        self.assertEqual(CandidateProfile.objects.count(), 2)
        self.assertEqual(EmployerProfile.objects.count(), 1)
        self.assertEqual(Skill.objects.count(), 4)
        self.assertEqual(CandidateSkill.objects.count(), 4)
        self.assertEqual(Job.objects.count(), 2)
        self.assertEqual(Application.objects.count(), 2)
        self.assertTrue(User.objects.get(username="user1").check_password("password"))


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

        self.recruiter_user = User.objects.create_user(username="recruiter1", password="password")
        UserProfile.objects.create(user=self.recruiter_user, role="recruiter")

    def test_candidate_can_add_skill_through_form(self):
        self.client.login(username="user1", password="password")
        response = self.client.post("/skills/add/", {"skill": self.skill.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CandidateSkill.objects.filter(candidate=self.candidate, skill=self.skill).exists())

    def test_duplicate_skill_is_not_created(self):
        CandidateSkill.objects.create(candidate=self.candidate, skill=self.skill)
        self.client.login(username="user1", password="password")
        response = self.client.post("/skills/add/", {"skill": self.skill.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You already added this skill.")
        self.assertEqual(CandidateSkill.objects.filter(candidate=self.candidate, skill=self.skill).count(), 1)

    def test_employer_can_create_job_through_form(self):
        self.client.login(username="adminfarm", password="password")
        response = self.client.post(
            "/jobs/add/",
            {
                "title": "Crop Supervisor",
                "description": "Oversee crop planning and field work",
                "location": "Tipperary",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Job.objects.filter(title="Crop Supervisor", employer=self.employer).exists())

    def test_candidate_can_apply_to_job_through_form(self):
        self.client.login(username="user1", password="password")
        response = self.client.post(f"/applications/add/{self.job.id}/", {}, follow=True)
        self.assertEqual(response.status_code, 200)
        application = Application.objects.get(candidate=self.candidate, job=self.job)
        self.assertEqual(application.status, "Pending")

    def test_duplicate_application_is_not_created(self):
        Application.objects.create(candidate=self.candidate, job=self.job, status="Pending")
        self.client.login(username="user1", password="password")
        response = self.client.post(f"/applications/add/{self.job.id}/", {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Application.objects.filter(candidate=self.candidate, job=self.job).count(), 1)

    def test_candidate_cannot_add_job(self):
        self.client.login(username="user1", password="password")
        response = self.client.get("/jobs/add/")
        self.assertEqual(response.status_code, 403)

    def test_employer_cannot_apply_for_job(self):
        self.client.login(username="adminfarm", password="password")
        response = self.client.get(f"/applications/add/{self.job.id}/")
        self.assertEqual(response.status_code, 403)

    def test_employer_sees_only_applications_for_their_jobs(self):
        other_employer_user = User.objects.create_user(username="farmtwo", password="password")
        UserProfile.objects.create(user=other_employer_user, role="employer")
        other_employer = EmployerProfile.objects.create(
            user=other_employer_user,
            company_name="Other Farm",
            location="Laois",
        )
        other_job = Job.objects.create(
            employer=other_employer,
            title="Other Job",
            description="Different employer job",
            location="Laois",
        )
        Application.objects.create(candidate=self.candidate, job=self.job, status="Pending")
        Application.objects.create(candidate=self.candidate, job=other_job, status="Pending")

        self.client.login(username="adminfarm", password="password")
        response = self.client.get("/applications/")
        self.assertEqual(response.status_code, 200)
        applications = list(response.context["applications"])
        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0].job, self.job)

    def test_recruiter_can_view_all_applications(self):
        second_job = Job.objects.create(
            employer=self.employer,
            title="Field Operator",
            description="Support seasonal farm activity",
            location="Cork",
        )
        Application.objects.create(candidate=self.candidate, job=self.job, status="Pending")
        Application.objects.create(candidate=self.candidate, job=second_job, status="Pending")

        self.client.login(username="recruiter1", password="password")
        response = self.client.get("/applications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["applications"].count(), 2)

    def test_candidate_applications_page_links_to_jobs(self):
        self.client.login(username="user1", password="password")
        response = self.client.get("/applications/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/jobs/"')
        self.assertNotContains(response, 'href="/applications/add/"')

    def test_employer_can_accept_application_for_their_job(self):
        application = Application.objects.create(candidate=self.candidate, job=self.job, status="Pending")
        self.client.login(username="adminfarm", password="password")
        response = self.client.post(
            f"/applications/{application.id}/status/",
            {"status": "Accepted"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.status, "Accepted")

    def test_recruiter_can_decline_application(self):
        application = Application.objects.create(candidate=self.candidate, job=self.job, status="Pending")
        self.client.login(username="recruiter1", password="password")
        response = self.client.post(
            f"/applications/{application.id}/status/",
            {"status": "Declined"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.status, "Declined")

    def test_candidate_cannot_update_application_status(self):
        application = Application.objects.create(candidate=self.candidate, job=self.job, status="Pending")
        self.client.login(username="user1", password="password")
        response = self.client.post(
            f"/applications/{application.id}/status/",
            {"status": "Accepted"},
        )
        self.assertEqual(response.status_code, 403)
        application.refresh_from_db()
        self.assertEqual(application.status, "Pending")

    def test_status_buttons_hidden_for_non_pending_application(self):
        Application.objects.create(candidate=self.candidate, job=self.job, status="Accepted")
        self.client.login(username="adminfarm", password="password")
        response = self.client.get("/applications/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'value="Accepted" class="btn btn-success btn-sm">Accept</button>')
        self.assertNotContains(response, 'value="Declined" class="btn btn-danger btn-sm">Decline</button>')