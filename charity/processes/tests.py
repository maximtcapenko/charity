from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from funds.models import Fund, VolunteerProfile
from .models import Process, ProcessState

class ProcessModelTest(TestCase):
    def setUp(self):
        self.fund = Fund.objects.create(name="Test Fund")
        self.user = User.objects.create_user(username="testuser")
        self.volunteer = VolunteerProfile.objects.create(user=self.user, fund=self.fund)

    def test_process_creation(self):
        process = Process.objects.create(
            name="Test Process",
            fund=self.fund,
            is_inactive=False
        )
        self.assertEqual(str(process), "Test Process")
        self.assertEqual(process.fund, self.fund)

    def test_process_state_creation(self):
        process = Process.objects.create(
            name="Test Process",
            fund=self.fund,
            is_inactive=False
        )
        state = ProcessState.objects.create(
            name="Test State",
            process=process,
            order_position=1,
            is_inactive=False
        )
        self.assertEqual(str(state), "Test State")
        self.assertEqual(state.process, process)
        self.assertEqual(state.order_position, 1)

class ProcessFormTest(TestCase):
    def setUp(self):
        self.fund = Fund.objects.create(name="Test Fund")

    def test_create_process_form_valid(self):
        from .forms import CreateProcessForm
        data = {
            'name': 'New Process',
            'fund': self.fund.id,
            'is_inactive': False
        }
        form = CreateProcessForm(data=data)
        self.assertTrue(form.is_valid())

    def test_create_process_state_form_valid(self):
        from .forms import CreateProcessStateForm
        process = Process.objects.create(
            name="Test Process",
            fund=self.fund,
            is_inactive=False
        )
        data = {
            'name': 'New State',
            'process': process.id,
            'is_approvement_required': False,
            'after_state': ''
        }
        form = CreateProcessStateForm(data=data, initial={'process': process})
        self.assertTrue(form.is_valid())
        state = form.save()
        self.assertEqual(state.order_position, 1)

    def test_create_process_state_form_ordering(self):
        from .forms import CreateProcessStateForm
        process = Process.objects.create(
            name="Test Process",
            fund=self.fund,
            is_inactive=False
        )
        state1 = ProcessState.objects.create(
            name="State 1",
            process=process,
            order_position=1
        )
        
        data = {
            'name': 'State 2',
            'process': process.id,
            'is_approvement_required': False,
            'after_state': ''
        }
        form = CreateProcessStateForm(data=data, initial={'process': process})
        self.assertTrue(form.is_valid())
        state2 = form.save()
        self.assertEqual(state2.order_position, 2)

        data = {
            'name': 'State 1.5',
            'process': process.id,
            'is_approvement_required': False,
            'after_state': state1.id
        }
        form = CreateProcessStateForm(data=data, initial={'process': process})
        self.assertTrue(form.is_valid())
        state1_5 = form.save()
        self.assertEqual(state1_5.order_position, 2)
        
        state2.refresh_from_db()
        self.assertEqual(state2.order_position, 3)

class ProcessViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.fund = Fund.objects.create(name="Test Fund")
        self.user = User.objects.create_user(username="testuser", password="password")
        self.volunteer = VolunteerProfile.objects.create(user=self.user, fund=self.fund)
        self.client.login(username="testuser", password="password")

    def test_get_list(self):
        url = reverse('processes:get_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'processes_list.html')

    def test_create_process_get(self):
        url = reverse('processes:create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_process_post(self):
        url = reverse('processes:create')
        data = {
            'name': 'New Process',
            'fund': self.fund.id,
            'is_inactive': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Process.objects.filter(name='New Process').exists())

    def test_get_details(self):
        process = Process.objects.create(name="Test Process", fund=self.fund, is_inactive=False)
        url = reverse('processes:get_details', args=[process.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'process_details.html')

    def test_edit_details_get(self):
        process = Process.objects.create(name="Test Process", fund=self.fund, is_inactive=False)
        url = reverse('processes:edit_details', args=[process.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_details_post(self):
        process = Process.objects.create(name="Test Process", fund=self.fund, is_inactive=False)
        url = reverse('processes:edit_details', args=[process.id])
        data = {
            'name': 'Updated Process',
            'fund': self.fund.id,
            'is_inactive': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        process.refresh_from_db()
        self.assertEqual(process.name, 'Updated Process')
        self.assertTrue(process.is_inactive)

    def test_create_state_get(self):
        process = Process.objects.create(name="Test Process", fund=self.fund, is_inactive=False)
        url = reverse('processes:create_state', args=[process.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_state_post(self):
        process = Process.objects.create(name="Test Process", fund=self.fund, is_inactive=False)
        url = reverse('processes:create_state', args=[process.id])
        data = {
            'name': 'New State',
            'process': process.id,
            'is_approvement_required': False,
            'after_state': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProcessState.objects.filter(name='New State', process=process).exists())

    def test_edit_state_details_get(self):
        process = Process.objects.create(name="Test Process", fund=self.fund, is_inactive=False)
        state = ProcessState.objects.create(name="Test State", process=process, order_position=1)
        url = reverse('processes:edit_state_details', args=[process.id, state.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_state_details_post(self):
        process = Process.objects.create(name="Test Process", fund=self.fund, is_inactive=False)
        state = ProcessState.objects.create(name="Test State", process=process, order_position=1)
        url = reverse('processes:edit_state_details', args=[process.id, state.id])
        data = {
            'name': 'Updated State',
            'process': process.id,
            'is_approvement_required': True,
            'after_state': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        state.refresh_from_db()
        self.assertEqual(state.name, 'Updated State')
        self.assertTrue(state.is_approvement_required)

    def test_edit_state_details_read_only_with_projects(self):
        from projects.models import Project
        process = Process.objects.create(name="Test Process", fund=self.fund, is_inactive=False)
        state = ProcessState.objects.create(name="Test State", process=process, order_position=1)
        
        project = Project.objects.create(
            name="Test Project",
            fund=self.fund,
            author=self.user,
            leader=self.user
        )
        project.processes.add(process)
        
        url = reverse('processes:edit_state_details', args=[process.id, state.id])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['read_only'])
        
        data = {
            'name': 'Should Not Update',
            'process': process.id,
            'is_approvement_required': True,
            'after_state': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        state.refresh_from_db()
        self.assertNotEqual(state.name, 'Should Not Update')
