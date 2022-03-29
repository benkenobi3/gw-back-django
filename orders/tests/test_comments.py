from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User, Group

from orders.enums import OrderState
from orders.models import Specialization, Order, Comment


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
        response = client.get(f'/api/comments/list?order={999}')
        self.assertEqual(response.status_code, 404)

        # Not possible to view
        client.force_login(self.other_employer)
        response = client.get(f'/api/comments/list?order={order.pk}')
        self.assertEqual(response.status_code, 403)

        # Not possible to view
        client.force_login(self.other_user)
        response = client.get(f'/api/comments/list?order={order.pk}')
        self.assertEqual(response.status_code, 403)

        # OK
        client.force_login(self.admin)
        response = client.get(f'/api/comments/list?order={order.pk}')
        self.assertEqual(response.status_code, 200)

        # OK
        client.force_login(self.main_employer)
        response = client.get(f'/api/comments/list?order={order.pk}')
        self.assertEqual(response.status_code, 200)

    def test_create_comment(self):
        client = Client()

        order = Order.objects.create(title='1', description='1', perf_spec=self.plumber_spec,
                                     customer=self.commenter, performer=self.main_employer)

        comments_count = order.comments.count()

        # Unauthorized
        response = client.post('/api/comments/create')
        self.assertEqual(response.status_code, 401)

        content_type = 'application/json'
        data = {'text': 'Hello', 'order': '999'}

        # 404
        client.force_login(self.other_employer)
        response = client.post(f'/api/comments/create', data, content_type)
        self.assertEqual(response.status_code, 404)

        data['order'] = order.pk

        # Not possible to comment
        client.force_login(self.other_employer)
        response = client.post(f'/api/comments/create', data, content_type)
        self.assertEqual(response.status_code, 403)

        # Not possible to comment
        client.force_login(self.other_user)
        response = client.post(f'/api/comments/create', data, content_type)
        self.assertEqual(response.status_code, 403)

        # OK
        client.force_login(self.admin)
        response = client.post(f'/api/comments/create', data, content_type)
        self.assertEqual(response.status_code, 201)

        # OK
        client.force_login(self.main_employer)
        response = client.post(f'/api/comments/create', data, content_type)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(order.comments.count(), comments_count+2)

    def test_update_and_delete_comment(self):
        client = Client()

        order = Order.objects.create(title='1', description='1', perf_spec=self.plumber_spec,
                                     customer=self.commenter, performer=self.main_employer)

        comment = Comment.objects.create(text='Hello', user=self.commenter, order=order)

        # Unauthorized
        response = client.post(f'/api/comments/{comment.pk}/update')
        self.assertEqual(response.status_code, 401)

        content_type = 'application/json'
        data = {'text': 'hello', 'user': comment.user.pk, 'order': comment.order.pk}

        # Not possible to comment
        client.force_login(self.other_user)
        response = client.post(f'/api/comments/{comment.pk}/update', data, content_type)
        self.assertEqual(response.status_code, 403)

        data['user'] = self.other_user.pk

        # Not possible to change order or user
        client.force_login(self.commenter)
        response = client.post(f'/api/comments/{comment.pk}/update', data, content_type)
        self.assertEqual(response.status_code, 403)

        data['user'] = self.commenter.pk

        # OK
        client.force_login(self.commenter)
        response = client.post(f'/api/comments/{comment.pk}/update', data, content_type)
        self.assertEqual(response.status_code, 200)

        order.status = OrderState.REJECTED
        order.save()

        # Not possible to change comments in rejected orders
        client.force_login(self.commenter)
        response = client.post(f'/api/comments/{comment.pk}/update', data, content_type)
        self.assertEqual(response.status_code, 403)

        order.status = OrderState.INFO_REQUIRED
        order.save()

        # Deleted
        client.force_login(self.commenter)
        response = client.post(f'/api/comments/{comment.pk}/delete', data, content_type)
        self.assertEqual(response.status_code, 204)
