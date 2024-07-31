from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


######################################################################
class UserMessage(models.Model):
    """
    Сообщения от пользователей на странице контакты
    """
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
    """
    Информационные карточки внизу страницы
    Адрес, Режим работы, карта местонахожения
    """
    title = models.CharField(max_length=50, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = 'Инфо-Карточку'
        verbose_name_plural = 'Инфо-Карточки'

    def __str__(self):
        return self.title


######################################################################
class News(models.Model):
    """
    Новости дома и района
    """
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
    """
    Информация о тсн:
    -Реквизиты
    -Правление
    """
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
    """
    Каталог с документами(категории для документов):
    -Собрания
    -Тарифы
    """
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
    """
    Документы:
    -Протоколы собраний с файлами
    """
    title = models.CharField(max_length=250, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name='Описание')
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
    """
    Модель для хранения данных о приборах учета (счетчиков)
    для отображения данных в личном кабинете
    """
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
    """
    Модель для хранения предидущих показаний загруженных от бухгалтера
    эти показания начислены в платежках
    """
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
    """
    Показания приборов учета переданные собственниками через личный кабинет
    """
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
class Zayavki(models.Model):
    """
    Заявки из личного кабинета
    для вызова сантехника, электрика и т.д.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    description = models.TextField(verbose_name="Описание")
    phone = models.CharField(max_length=17, verbose_name='Телефон', blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")
    date_completed = models.DateTimeField(blank=True, null=True, verbose_name="Дата выполнения")
    TYPE_SELECT = (
        ('0', 'Выполнено'),
        ('1', 'В работе'),
        ('2', 'Ожидание'),
    )
    status = models.CharField(max_length=3, default='2', choices=TYPE_SELECT, verbose_name='Статус', blank=True)

    class Meta:
        verbose_name = 'Заявку от собственника'
        verbose_name_plural = 'Заявки от собственников'

    def __str__(self):
        return f"Заявка от {self.user.username}"
######################################################################
