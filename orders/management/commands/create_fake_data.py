from collections import namedtuple
from random import choice

from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group

from orders.models import Specialization, Order


class Command(BaseCommand):

    def __init__(self):
        super().__init__()

        self.admin = Group.objects.get(name='admin')
        self.service = Group.objects.get(name='service_employee')

        self.specs = [
            Specialization.objects.get(name='carpenter', title='Плотник'),
            Specialization.objects.get(name='plumber', title='Сантехник'),
            Specialization.objects.get(name='electrician', title='Электрик'),
        ]

        self.password = '123'

    def create_employers(self):

        users = [
            User.objects.get_or_create(username='vp', email='email@vp.ru', password=self.password, first_name='Вадим', last_name='Петров'),
            User.objects.get_or_create(username='ks', email='email@ks.ru', password=self.password, first_name='Константин', last_name='Степанов'),
            User.objects.get_or_create(username='dk', email='email@dk.ru', password=self.password, first_name='Дмитрий', last_name='Кудряшов'),
            User.objects.get_or_create(username='yc', email='email@yc.ru', password=self.password, first_name='Ярослав', last_name='Чернышев'),
            User.objects.get_or_create(username='mm', email='email@mm.ru', password=self.password, first_name='Матвей', last_name='Малышев'),
            User.objects.get_or_create(username='tk', email='email@tk.ru', password=self.password, first_name='Тимофей', last_name='Краснов'),
            User.objects.get_or_create(username='mf', email='email@mf.ru', password=self.password, first_name='Максим', last_name='Филиппов'),
        ]

        for user, created in users:
            if created:
                self.service.user_set.add(user)
                user.profile.spec = choice(self.specs)
                user.save()

        return [user for user, _ in users]

    def create_simple_users(self):

        users = [
            User.objects.get_or_create(username='ds', email='email@ds.ru', password=self.password, first_name='Данила', last_name='Свиридов'),
            User.objects.get_or_create(username='lv', email='email@lv.ru', password=self.password, first_name='Лев', last_name='Васильев'),
            User.objects.get_or_create(username='bs', email='email@bs.ru', password=self.password, first_name='Богдан', last_name='Сергеев'),
            User.objects.get_or_create(username='mg', email='email@mg.ru', password=self.password, first_name='Максим', last_name='Голубев'),
            User.objects.get_or_create(username='nc', email='email@nc.ru', password=self.password, first_name='Назар', last_name='Черкасов'),
            User.objects.get_or_create(username='at', email='email@at.ru', password=self.password, first_name='Артём', last_name='Титов'),
            User.objects.get_or_create(username='ab', email='email@ab.ru', password=self.password, first_name='Андрей', last_name='Балашов'),
            User.objects.get_or_create(username='do', email='email@do.ru', password=self.password, first_name='Даниил', last_name='Козлов'),
            User.objects.get_or_create(username='ts', email='email@ts.ru', password=self.password, first_name='Тимофей', last_name='Седов'),
            User.objects.get_or_create(username='rz', email='email@rz.ru', password=self.password, first_name='Роман', last_name='Злобин'),
            User.objects.get_or_create(username='dt', email='email@dt.ru', password=self.password, first_name='Даниил', last_name='Трошин'),
            User.objects.get_or_create(username='av', email='email@av.ru', password=self.password, first_name='Артём', last_name='Власов'),
            User.objects.get_or_create(username='fl', email='email@fl.ru', password=self.password, first_name='Фёдор', last_name='Лукьянов'),
            User.objects.get_or_create(username='ge', email='email@ge.ru', password=self.password, first_name='Глеб', last_name='Еремеев'),
        ]

        return [user for user, _ in users]

    @staticmethod
    def create_orders(users, employers):

        problem = namedtuple('problem', ['title', 'description'])

        problems = {
            'plumber': [
                problem('Капающий кран', 'Постоянно капает кран на кухне'),
                problem('Слабо течет вода', 'В ванной вода в душе стала течь слишком слабо'),
                problem('Неисправный бачок в туалете', 'После смывания вода не останавливается, а продолжает вытекать'),
                problem('Подтекающие батарея', 'Батарея в комнате капает на пол'),
                problem('Забитая раковина', 'Вода не уходит из раковины')
            ],
            'carpenter': [
                problem('Не закрывается дверь', 'Сломался замок на двери, нужен новый'),
                problem('Отвалилась дверца тумбочки', 'Отвалилась дверца тумбочки. Одну петлю выкинули'),
                problem('Дверь сошла с петель', 'Дверь в ванной комнате сошла с петель'),
                problem('Упал подоконник', 'После того как на подоконник облокотились, он упал'),
                problem('Дует из окна', 'ДУет из окна, во время дождя просачивается вода'),
            ],
            'electrician': [
                problem('Искрит розетка', 'При подключении и отключении любого прибора видны искры'),
                problem('Проверка холодильника', 'Купили новый холодильник. Нужно проверить, что он подходит'),
                problem('Открытая розетка', 'Из одной розетки торчат провода'),
                problem('Перепады электричества', 'В квартире очень часто лампочки то тускло горят, то очень ярко'),
                problem('Нет света', 'После того как к нам провели интернет, пропал свет, совсем'),
            ]
        }

        orders = []

        for user in users:
            employer = choice(employers)
            spec = employer.profile.spec
            problem = choice(problems[spec.name])

            order = Order(title=problem.title, description=problem.description,
                          customer=user, performer=employer, perf_spec=spec)
            orders.append(order)

        Order.objects.bulk_create(orders)

        return orders

    def handle(self, *args, **options):
        employers = self.create_employers()
        users = self.create_simple_users()
        self.create_orders(users, employers)
