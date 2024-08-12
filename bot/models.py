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
    user_id = models.IntegerField()
    username = models.CharField(max_length=100, blank=True, default=None)
    datetime = models.DateTimeField(auto_now_add=True)
    ls = models.IntegerField()
    kv = models.IntegerField()

    def __str__(self):
        return str(self.user_id)
    class Meta:
        verbose_name = 'Пользователи бота'
        verbose_name_plural = 'Пользователи бота'