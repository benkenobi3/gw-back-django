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