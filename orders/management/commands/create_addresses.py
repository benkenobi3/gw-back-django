from django.core.management import BaseCommand
from orders.models import Address


class Command(BaseCommand):

    def handle(self, *args, **options):
        l1 = Address.objects.get_or_create(pk=1, name='Общежитие №1 Московского Политеха', location='-')
        l2 = Address.objects.get_or_create(pk=2, name='Общежитие №2 Московского Политеха', location='-')
        l3 = Address.objects.get_or_create(pk=3, name='Общежитие №3 Московского Политеха', location='-')
        l4 = Address.objects.get_or_create(pk=4, name='Общежитие №4 Московского Политеха', location='800-летия Москвы 28к1')
        l5 = Address.objects.get_or_create(pk=5, name='Общежитие №5 Московского Политеха', location='-')
        l6 = Address.objects.get_or_create(pk=6, name='Общежитие №6 Московского Политеха', location='-')
        l7 = Address.objects.get_or_create(pk=7, name='Общежитие №7 Московского Политеха', location='-')
        l8 = Address.objects.get_or_create(pk=8, name='Общежитие №8 Московского Политеха', location='-')
        l9 = Address.objects.get_or_create(pk=9, name='Общежитие №9 Московского Политеха', location='-')
        l10 = Address.objects.get_or_create(pk=10, name='Общежитие №10 Московского Политеха', location='-')

