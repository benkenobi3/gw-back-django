from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from orders.enums import OrderState
from orders.models import Order, Comment, TimelinePoint, Profile, Specialization
from orders.permissions import IsAdminOrServiceEmployeeUser, \
    IsAllowToSeeOrderComments, IsAdminOrServiceEmployeeOrCustomer, \
    IsAdminOrServiceEmployeeOrSelf, IsAllowToEditOrDeleteComments
from orders.serializers import OrderSerializer, CommentSerializer, UserSerializer, \
    OrderStatusUpdateSerializer, OrderPerformerUpdateSerializer, OrderCreateSerializer,\
    CommentCreationSerializer, TimelinePointSerializer, SpecSerializer


class OrderPk(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeOrCustomer]


class Orders(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]


class UserPk(generics.RetrieveAPIView):
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeOrSelf]


class UserOrders(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.orders_as_customer


class Employers(generics.ListAPIView):
    queryset = User.objects.filter(groups__name__in=['service_employee']).select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]


class AvailableEmployers(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]

    def list(self, request, *args, **kwargs):
        order = Order.objects.get(pk=request.GET['order'])
        queryset = User.objects.select_related('profile').filter(profile__spec_id=order.perf_spec.pk)
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)


class StatusChanger(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]

    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)
        title = f'Статус заявки изменен на "{res.data["status_locale"]}"'
        TimelinePoint.objects.create(order=self.get_object(), title=title)
        return res


class PerformerChanger(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderPerformerUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]

    def get_serializer_context(self):
        return {
            'user': self.request.user,
            'order_spec': self.get_object().perf_spec
        }

    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)
        performer = User.objects.get(pk=res.data['performer'])
        title = f'Назначен новый исполнитель - {performer.first_name} {performer.last_name}'
        TimelinePoint.objects.create(order=self.get_object(), title=title)
        return res


class CreateOrder(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        request.data['customer'] = str(request.user.pk)
        return super().post(request, *args, **kwargs)


class Comments(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentCreationSerializer
    permission_classes = [IsAuthenticated, IsAllowToSeeOrderComments]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(order__pk=request.GET['order'], is_active=True)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # TODO можно создать комментарий в закрытой заявке, но нельзя отредактировать его
        request.data['user'] = request.user.pk
        return super().create(request, *args, **kwargs)


class CommentsUpdate(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAllowToEditOrDeleteComments]

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.is_active = False
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        request.data['was_edited'] = True
        return super().update(request, *args, **kwargs)


class TimelinePoints(generics.ListAPIView):
    serializer_class = TimelinePointSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = TimelinePoint.objects.filter(order__pk=request.GET['order'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StatusList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        status_list = [{'status_locale': OrderState.ru(s[0]), 'status': s[0]} for s in OrderState.choices]
        return Response(status_list)


class SpecializationList(generics.ListAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecSerializer
    permission_classes = [IsAuthenticated]


class BusyChart(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]

    @staticmethod
    def get_data_for_doughnut(busy, free):
        return {
            'labels': ['Заняты', 'Свободны'],
            'datasets': [{
                'label': 'dataset',
                'data': [busy, free],
                'backgroundColor': [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)'
                ]
            }]
        }

    def list(self, request, *args, **kwargs):

        chart_list = []

        spec_titles = ['Плотник', 'Электрик', 'Сантехник']

        all_employers = Profile.objects.filter(spec__title__in=spec_titles).prefetch_related('spec')
        busy_employers = [employer for employer in all_employers if employer.is_busy]

        chart_list.append({
            'title': 'Все сотрудники',
            'data': self.get_data_for_doughnut(len(busy_employers), len(all_employers) - len(busy_employers))
        })

        for title in spec_titles:
            emp = [employer for employer in all_employers if employer.spec.title == title]
            busy_emp = [employer for employer in emp if employer.is_busy]

            chart_list.append({
                'title': title + 'и',
                'data': self.get_data_for_doughnut(len(busy_emp), len(emp) - len(busy_emp))
            })

        return Response(chart_list)


class StatusChart(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]

    @staticmethod
    def get_data_for_radar(data):
        return {
            'labels': ['Создана', 'Назначена', 'В работе', 'Требуется информация', 'Завершена', 'Отклонена'],
            'datasets': [{
                'label': 'Статусы заявок',
                'fill': True,
                'data': data,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgb(255, 99, 132)',
                'pointBackgroundColor': 'rgb(255, 99, 132)',
                'pointBorderColor': '#fff',
                'pointHoverBackgroundColor': '#fff',
                'pointHoverBorderColor': 'rgb(255, 99, 132)'
            }]
        }

    def retrieve(self, request, *args, **kwargs):
        counters = Order.objects.all().values('status').annotate(total=Count('status'))

        values = {el[0]: 0 for el in OrderState.choices}
        for counter in counters:
            values[counter['status']] = counter['total']

        result = self.get_data_for_radar(list(values.values()))
        return Response(result)
