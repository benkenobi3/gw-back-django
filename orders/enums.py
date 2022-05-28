from django.db.models import enums


class OrderState(enums.TextChoices):
    CREATED = 'created'
    APPOINTED = 'appointed'
    ACCEPTED = 'accepted'
    INFO_REQUIRED = 'info_required'
    DONE = 'done'
    REJECTED = 'rejected'

    @staticmethod
    def ru(order_state):
        dictionary = {
            'created': 'создана',
            'appointed': 'назначена',
            'accepted': 'в\u00a0работе',
            'info_required': 'требуется\u00a0информация',
            'done': 'завершена',
            'rejected': 'отклонена',
        }
        return dictionary[order_state]


class DocumentType(enums.TextChoices):
    PDF = 'pdf'
