from random import choice, randint
from django.core.management import BaseCommand
from orders.models import Order, Image


class Command(BaseCommand):

    def __init__(self):
        super().__init__()

        self.urls = [
            'http://localhost:3000/cats/c1.jpg',
            'http://localhost:3000/cats/c2.jpg',
            'http://localhost:3000/cats/c3.jpg',
            'http://localhost:3000/cats/c4.jpg',
            'http://localhost:3000/cats/c5.jpg'
        ]

    def append_images_to_orders(self):

        orders = Order.objects.all()

        for order in orders:
            for i in range(randint(0, 5)+1):
                Image.objects.create(url=choice(self.urls), order=order)

    def handle(self, *args, **options):
        self.append_images_to_orders()
