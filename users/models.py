from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    fio = models.CharField(max_length=200, verbose_name='ФИО', blank=True)
    kv = models.IntegerField(verbose_name='Квартира', blank=True, default=0)
    ls = models.IntegerField(verbose_name='Лицевой счет', blank=True, default=0)
    address = models.CharField(max_length=250, verbose_name='Адрес', blank=True)
    sq = models.CharField(max_length=10, verbose_name='Площадь', blank=True)
    phone = models.CharField(max_length=17, verbose_name='Телефон', blank=True)
    TYPE_SELECT = (
        (False, 'Бумажный'),
        (True, 'E-mail'),
    )
    rec_doc = models.BooleanField(default=False, choices=TYPE_SELECT, verbose_name="Способ получения платежных "
                                                                               "документов", blank=True)
    check_email = models.BooleanField(default=False, verbose_name='Проверка email', blank=True)

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'
        ordering = ['kv']


######################################################################
class Receipts(models.Model):
    # kv = models.IntegerField(verbose_name="Квартира")
    ls = models.IntegerField(verbose_name='Лицевой счет', blank=True, default=0)
    date = models.DateField(verbose_name='Закакой месяц')
    file = models.FileField(upload_to="receipts/", verbose_name="Квитанция")
    show = models.IntegerField(verbose_name="Кол-во скачиваний", default=0)

    class Meta:
        verbose_name = 'Квитанции'
        verbose_name_plural = 'Квитанции'
        ordering = ['ls']
    def __str__(self):
        return f"Платежка л.сч: {self.ls}"
######################################################################

######################################################################
