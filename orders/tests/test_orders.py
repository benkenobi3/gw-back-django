from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User, Group

from orders.models import Specialization, Order


class OrdersTestCase(TestCase):

    def setUp(self) -> None:

        # Prepare DB
        call_command('create_specs')
        call_command('create_groups')

        self.user = User.objects.create_user(username='User', email='user@email.com')
        self.admin = User.objects.create_user(username='Admin', email='admin@email.com')
        self.employer = User.objects.create_user(username='Employer', email='employer@email.com')

        # Groups
        admin_group = Group.objects.get(name='admin')
        employer_group = Group.objects.get(name='service_employee')

        admin_group.user_set.add(self.admin)
        employer_group.user_set.add(self.employer)

        # Specs
        self.plumber_spec = Specialization.objects.get(name='plumber')

        self.employer.profile.spec = self.plumber_spec
        self.employer.save()

    def test_all_list(self):
        client = Client()

        # Unauthorized
        response = client.get('/api/orders/all')
        self.assertEqual(response.status_code, 401)

        # Has not permissions
        client.force_login(user=self.user)
        response = client.get('/api/orders/all')
        self.assertEqual(response.status_code, 403)

        # OK
        client.force_login(user=self.admin)
        response = client.get('/api/orders/all')
        self.assertEqual(response.status_code, 200)

    def test_my_list(self):
        client = Client()

        # Unauthorized
        response = client.get('/api/orders/list')
        self.assertEqual(response.status_code, 401)

        # Empty list
        client.force_login(user=self.user)
        response = client.get('/api/orders/list')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        order = Order.objects.create(title='1', description='1', perf_spec=self.plumber_spec, customer=self.employer)
        user_order = Order.objects.create(title='2', description='2', perf_spec=self.plumber_spec, customer=self.user)

        # One user order
        client.force_login(user=self.user)
        response = client.get('/api/orders/list')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        client.force_login(user=self.employer)
        response = client.get('/api/orders/list')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
