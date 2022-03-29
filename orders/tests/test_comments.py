from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User, Group

from orders.models import Specialization, Order
from orders.enums import OrderState


class CommentsTestCase(TestCase):

    def setUp(self) -> None:

        # Prepare DB
        call_command('create_specs')
        call_command('create_groups')

        self.admin = User.objects.create_user(username='Admin', email='admin@email.com')
        self.commenter = User.objects.create_user(username='Commenter', email='commenter@email.com')
        self.other_user = User.objects.create_user(username='Other User', email='otheruser@email.com')
        self.main_employer = User.objects.create_user(username='Main Employer', email='employer1@email.com')
        self.other_employer = User.objects.create_user(username='Other Employer', email='employer2@email.com')

        # Groups
        admin_group = Group.objects.get(name='admin')
        employer_group = Group.objects.get(name='service_employee')

        admin_group.user_set.add(self.admin)
        employer_group.user_set.add(self.main_employer)
        employer_group.user_set.add(self.other_employer)

        # Specs
        self.plumber_spec = Specialization.objects.get(name='plumber')

        self.main_employer.profile.spec = self.plumber_spec
        self.main_employer.save()

        self.other_employer.profile.spec = self.plumber_spec
        self.other_employer.save()

    def test_comments_list(self):
        client = Client()

        order = Order.objects.create(title='1', description='1', perf_spec=self.plumber_spec,
                                     customer=self.commenter, performer=self.main_employer)

        # Unauthorized
        response = client.get('/api/comments/list')
        self.assertEqual(response.status_code, 401)

        # 404
        client.force_login(self.other_employer)
        response = client.get(f'/api/orders/comments/list?order={999}')
        self.assertEqual(response.status_code, 404)

        # Not possible to view
        client.force_login(self.other_employer)
        response = client.get(f'/api/orders/comments/list?order={order.pk}')
        self.assertEqual(response.status_code, 403)

        # Not possible to view
        client.force_login(self.other_user)
        response = client.get(f'/api/orders/comments/list?order={order.pk}')
        self.assertEqual(response.status_code, 403)

        # OK
        client.force_login(self.admin)
        response = client.get(f'/api/orders/comments/list?order={order.pk}')
        self.assertEqual(response.status_code, 200)

        # OK
        client.force_login(self.main_employer)
        response = client.get(f'/api/orders/comments/list?order={order.pk}')
        self.assertEqual(response.status_code, 200)
