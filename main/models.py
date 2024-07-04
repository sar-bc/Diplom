from django.db import models
from django.utils import timezone


######################################################################
class UserMessage(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email', blank=True)
    phone = models.CharField(max_length=17, verbose_name='Телефон', blank=True)
    message = models.TextField(verbose_name='Сообщение')
    time_created = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сообщения'
        verbose_name_plural = 'Сообщения'


######################################################################
class Card(models.Model):
    title = models.CharField(max_length=50, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = 'Footer Карточку'
        verbose_name_plural = 'Footer Карточки'

    def __str__(self):
        return self.title


######################################################################
class News(models.Model):
    title = models.CharField(max_length=250, verbose_name='Заголовок новости')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    body = models.TextField(verbose_name='Новость', blank=True)
    publish = models.DateTimeField(default=timezone.now, verbose_name="Создано")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    img = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name='Фото', blank=True)
    file = models.FileField(upload_to="files/%Y/%m/%d/", verbose_name="Файл", blank=True)
    is_publihed = models.BooleanField(default=True, verbose_name="Статус")
    views = models.IntegerField(verbose_name="Просмотры", default=0)

    def get_absolute_url(self):
        return '/news/{}/'.format(self.slug)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-publish']


######################################################################
class Info(models.Model):
    title = models.CharField(max_length=250, verbose_name='Заголовок Информации')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(verbose_name='Информация', blank=True)
    file = models.FileField(upload_to="files/%Y/%m/%d/", verbose_name="Файл", blank=True)
    publish = models.DateTimeField(default=timezone.now, verbose_name="Создано")
    views = models.IntegerField(verbose_name="Просмотры", default=0)

    def get_absolute_url(self):
        return '/info/{}/'.format(self.slug)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Информация о ТСН'
        verbose_name_plural = 'Информация о ТСН'
        ordering = ['-publish']


######################################################################
class KatDoc(models.Model):
    name = models.CharField(max_length=250, verbose_name='Заголовок категории')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def get_absolute_url(self):
        return '/docs/{}/'.format(self.slug)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категории - Документы'
        verbose_name_plural = 'Категории - Документы'


######################################################################
class Doc(models.Model):
    title = models.CharField(max_length=250, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.CharField(max_length=250, blank=True, verbose_name='Описание')
    file = models.FileField(upload_to="files/%Y/%m/%d/", verbose_name="Файл", blank=True)
    publish = models.DateTimeField(default=timezone.now, verbose_name="Создано")
    created = models.DateTimeField(auto_now_add=True)
    kat_id = models.ForeignKey('KatDoc', on_delete=models.PROTECT, verbose_name="Категории")
    views = models.IntegerField(verbose_name="Просмотры", default=0)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-publish']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/doc/{}/'.format(self.slug)
    ######################################################################


class MeterDev(models.Model):
    kv = models.IntegerField(verbose_name='Квартира')
    name = models.CharField(max_length=250, verbose_name='Наименование ПУ')
    number = models.CharField(max_length=100, verbose_name='Заводской номер', unique=True)
    data_pov_next = models.DateField(verbose_name='Дата следующей поверки')
    plomba = models.CharField(max_length=100, verbose_name='Пломба', blank=True)
    amg = models.CharField(max_length=100, verbose_name='Антимагнитная пломба', blank=True)
    pokazaniya = models.CharField(max_length=100, verbose_name='Начальные показания', blank=True)
    date_akt = models.DateField(verbose_name='Дата акта', blank=True)
    TYPE_SELECT = (
        ('hv', 'ХВ'),
        ('gv', 'ГВ'),
        ('e', 'ЭЛ'),
    )
    type = models.CharField(max_length=3, default='hv', choices=TYPE_SELECT, verbose_name='Тип счетчика', blank=True)

    class Meta:
        verbose_name = 'Прибор учета'
        verbose_name_plural = 'Приборы учета'

    def __str__(self):
        return str(self.kv)
######################################################################
class Pokazaniya(models.Model):
    kv = models.IntegerField(verbose_name='Квартира')
    hv = models.CharField(max_length=25, verbose_name='Холодная вода', blank=True)
    gv = models.CharField(max_length=25, verbose_name='Горячая вода', blank=True)
    e = models.CharField(max_length=25, verbose_name='Электричество', blank=True)
    date = models.DateField(verbose_name='Дата показаний')

    class Meta:
        verbose_name = 'Показание ИПУ'
        verbose_name_plural = 'Показания ИПУ'

    def __str__(self):
        return str(self.kv)

######################################################################
class PokazaniyaUser(models.Model):
    kv = models.IntegerField(verbose_name='Квартира')
    hv = models.CharField(max_length=25, verbose_name='Холодная вода', blank=True)
    gv = models.CharField(max_length=25, verbose_name='Горячая вода', blank=True)
    e = models.CharField(max_length=25, verbose_name='Электричество', blank=True)
    date = models.DateField(auto_now_add=True, verbose_name='Дата показаний')

    class Meta:
        verbose_name = 'Показание собственника'
        verbose_name_plural = 'Показания собственников'

    def __str__(self):
        return str(self.kv)
######################################################################

