from django.urls import re_path
from orders.views import Orders


urlpatterns = [
    re_path('orders/', Orders.as_view(), name='orders-list')
]
