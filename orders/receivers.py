from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from orders.models import Order, TimelinePoint, Profile


@receiver(post_save, sender=Order)
def create_order(sender, instance, created, **kwargs):
    if created:
        TimelinePoint.objects.create(order=instance, title='Заявка создана')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
