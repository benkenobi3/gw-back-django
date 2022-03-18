from django.db import models
from django.contrib.auth.models import User
from orders.enums import OrderState


class Order(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.TextField()
    creation_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, null=False, default=OrderState.CREATED, choices=OrderState.choices)

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_customer')
    performer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='orders_as_performer')

    def __str__(self):
        return self.title
