from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.enums import OrderState, DocumentType


class Specialization(models.Model):
    name = models.CharField(max_length=100, null=False)
    title = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.title


class Order(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.TextField()
    creation_datetime = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, null=False, default=OrderState.CREATED, choices=OrderState.choices)

    perf_spec = models.ForeignKey(Specialization, on_delete=models.SET_DEFAULT, related_name='orders', default=1)

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_customer')
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


class Comment(models.Model):
    text = models.TextField()
    creation_datetime = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='comments')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spec = models.ForeignKey(Specialization, on_delete=models.SET_DEFAULT, related_name='performers', default=1)

    @staticmethod
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @staticmethod
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    @property
    def is_busy(self):
        progress_statuses = [OrderState.APPOINTED, OrderState.ACCEPTED, OrderState.INFO_REQUIRED]
        orders_in_progress = self.user.orders_as_performer.filter(status__in=progress_statuses)
        return bool(orders_in_progress)

    def __str__(self):
        return self.user.username
