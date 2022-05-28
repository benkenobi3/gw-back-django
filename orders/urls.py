from django.urls import re_path
from orders.views import Orders, UserOrders, \
    StatusChanger, PerformerChanger, CreateOrder, \
    Comments, Employers, OrderPk, UserPk, AvailableEmployers, CommentsUpdate, StatusList


urlpatterns = [
    re_path('users/(?P<pk>.*)', UserPk.as_view(), name='users-retrieve'),
    re_path('employers/all', Employers.as_view(), name='employers-list'),
    re_path('employers/available', AvailableEmployers.as_view(), name='orders-employers'),  # ?order=

    re_path('orders/all', Orders.as_view(), name='orders-list'),
    re_path('orders/list', UserOrders.as_view(), name='orders-user-list'),
    re_path('orders/create', CreateOrder.as_view(), name='orders-create'),
    re_path('orders/status-list', StatusList.as_view(), name='status-list'),
    re_path('orders/(?P<pk>.*)/$', OrderPk.as_view(), name='orders-retrieve'),
    re_path('orders/(?P<pk>.*)/status$', StatusChanger.as_view({'get': 'retrieve', 'post': 'update'})),
    re_path('orders/(?P<pk>.*)/performer$', PerformerChanger.as_view({'get': 'retrieve', 'post': 'update'})),

    re_path('comments/list', Comments.as_view({'get': 'list'}), name='orders-comments-list'),  # ?order=
    re_path('comments/create', Comments.as_view({'post': 'create'}), name='orders-comments-create'),
    re_path('comments/(?P<pk>.*)/update', CommentsUpdate.as_view({'post': 'update'}), name='orders-comments-update'),
    re_path('comments/(?P<pk>.*)/delete', CommentsUpdate.as_view({'post': 'destroy'}), name='orders-comments-delete'),
]
