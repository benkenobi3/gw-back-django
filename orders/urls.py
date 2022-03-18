from django.urls import re_path
from orders.views import OrderListAPIView


urlpatterns = [
    re_path('orders/', OrderListAPIView.as_view(), name='orders-list')
]
