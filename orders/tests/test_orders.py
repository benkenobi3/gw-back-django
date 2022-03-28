from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User, Group

from orders.models import Specialization, Order
from orders.enums import OrderState


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
        self.carpenter_spec = Specialization.objects.get(name='carpenter')

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

    def test_order_create(self):
        client = Client()

        # Unauthorized
        response = client.post('/api/orders/create')
        self.assertEqual(response.status_code, 401)

        client.force_login(user=self.user)
        orders_count = Order.objects.all().count()

        # Empty data
        response = client.post('/api/orders/create', data={}, content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # Empty nested data
        data = {
            'title': 'user-order',
            'description': 'user-order-description',
            'perf_spec': self.plumber_spec.pk,
            'images': []
        }

        response = client.post('/api/orders/create', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # Wrong nested data
        data = {
            'title': 'user-order',
            'description': 'user-order-description',
            'perf_spec': self.plumber_spec.pk,
            'images': [
                {'url': 'url'},
                {'url2': 'url2'}
            ]
        }

        response = client.post('/api/orders/create', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # OK
        data = {
            'title': 'user-order',
            'description': 'user-order-description',
            'perf_spec': self.plumber_spec.pk,
            'images': [
                {'url': 'https://image-url/1'},
                {'url': 'https://image-url/2'},
            ]
        }

        response = client.post('/api/orders/create', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.all().count(), orders_count+1)

    def test_order_status_changer(self):
        client = Client()

        order = Order.objects.create(title='2', description='2', perf_spec=self.plumber_spec, customer=self.user)

        # Unauthorized
        response = client.get('/api/orders/1/status')
        self.assertEqual(response.status_code, 401)

        # Permission denied
        client.force_login(user=self.user)
        response = client.get('/api/orders/1/status')
        self.assertEqual(response.status_code, 403)

        # OK get
        client.force_login(user=self.employer)
        response = client.get('/api/orders/1/status')
        self.assertEqual(response.status_code, 200)

        data = {'status': OrderState.REJECTED}

        # OK post
        client.force_login(user=self.employer)
        response = client.post('/api/orders/1/status', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_order_performer_changer(self):
        client = Client()

        order = Order.objects.create(title='2', description='2', perf_spec=self.carpenter_spec, customer=self.user)

        # Unauthorized
        response = client.get('/api/orders/1/performer')
        self.assertEqual(response.status_code, 401)

        # Permission denied
        client.force_login(user=self.user)
        response = client.get('/api/orders/1/performer')
        self.assertEqual(response.status_code, 403)

        # OK get
        client.force_login(user=self.employer)
        response = client.get('/api/orders/1/performer')
        self.assertEqual(response.status_code, 200)

        data = {'performer': self.admin.pk}

        # Not possible to take an order from another spec
        client.force_login(user=self.employer)
        response = client.post('/api/orders/1/performer', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 400)

        order.perf_spec = self.plumber_spec
        order.save()

        # Can not set anybody except yourself
        client.force_login(user=self.employer)
        response = client.post('/api/orders/1/performer', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['performer'], self.employer.pk)

        # OK post
        client.force_login(user=self.admin)
        response = client.post('/api/orders/1/performer', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['performer'], self.admin.pk)

        data['performer'] = self.employer.pk

        # OK post
        client.force_login(user=self.admin)
        response = client.post('/api/orders/1/performer', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['performer'], self.employer.pk)
