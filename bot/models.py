from django.db import models


# Create your models here.
class UsersBot(models.Model):
    """
    модель для хранения данных пользователей бота
    user_id 12345667
    username
    datetime дата
    ls список лицевых ['123445678','87654321']
    """
    user_id = models.BigIntegerField(verbose_name='ID Telegram')
    username = models.CharField(max_length=100, blank=True, default=None, verbose_name='Имя пользователя telegram')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления лицевого')
    ls = models.IntegerField(verbose_name='Лицевой счет')
    kv = models.IntegerField(verbose_name='Квартира')

    def __str__(self):
        return str(self.user_id)

    class Meta:
        verbose_name = 'Пользователи бота'
        verbose_name_plural = 'Пользователи бота'
