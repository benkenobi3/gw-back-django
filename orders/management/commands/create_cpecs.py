from django.core.management import BaseCommand
from orders.models import Specialization


class Command(BaseCommand):

    def handle(self, *args, **options):
        not_defined = Specialization.objects.get_or_create(pk=1, name='not_defined', title='Нет специализации')
        carpenter = Specialization.objects.get_or_create(name='carpenter', title='Плотник')
        plumber = Specialization.objects.get_or_create(name='plumber', title='Сантехник')
        electrician = Specialization.objects.get_or_create(name='electrician', title='Электрик')
