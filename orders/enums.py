from django.db.models import enums


class OrderState(enums.TextChoices):
    CREATED = 'created'
    APPOINTED = 'appointed'
    ACCEPTED = 'accepted'
    INFO_REQUIRED = 'info_required'
    DONE = 'done'
    REJECTED = 'rejected'
