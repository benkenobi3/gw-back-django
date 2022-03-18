from django.core.management import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):

    def handle(self, *args, **options):
        admin = Group.objects.get_or_create(name='admin')
        service_employee = Group.objects.get_or_create(name='service_employee')
