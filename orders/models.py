from django.db import models
from django.contrib.auth.models import User
from orders.enums import OrderState, DocumentType


class Order(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.TextField()
    creation_datetime = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, null=False, default=OrderState.CREATED, choices=OrderState.choices)

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_customer', null=True)
    performer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='orders_as_performer', null=True)

    def __str__(self):
        return self.title


class Image(models.Model):
    url = models.CharField(max_length=500, null=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='images')


class Document(models.Model):
    url = models.CharField(max_length=500, null=False)
    document_type = models.CharField(max_length=20, null=False, default=DocumentType.PDF, choices=DocumentType.choices)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='documents')
