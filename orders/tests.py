from django.test import TestCase
from django.test.client import Client


class UserTestCase(TestCase):

    def setUp(self) -> None:
        client = Client()

    def test_order_creation(self):
        pass
