import os
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import *
from .forms import MeterImportForm
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import path
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.conf import settings
import csv
##########################################################
# Для кастомной админки
from bot.models import UsersBot
from bot.admin import UsersBotAdmin

from users.models import User, Receipts
from users.admin import UserAdmin, ReceiptsAdmin


##########################################################
# admin.site.site_title = 'Админ-панель ТСН'
# admin.site.site_header = 'Админ-панель ТСН'


##########################################################
class MonthDevFilter(admin.SimpleListFilter):
    title = 'Месяц следующей поверки '
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        months = [
            (1, 'Январь'),
            (2, 'Февраль'),
            (3, 'Март'),
            (4, 'Апрель'),
            (5, 'Май'),
            (6, 'Июнь'),
            (7, 'Июль'),
            (8, 'Август'),
            (9, 'Сентябрь'),
            (10, 'Октябрь'),
            (11, 'Ноябрь'),
            (12, 'Декабрь'),
        ]
        return months

    def queryset(self, request, queryset):
        if self.value():
            month = int(self.value())
            year = timezone.now().year  # Или можете использовать другой год
            return queryset.filter(data_pov_next__month=month, data_pov_next__year=year)
        return queryset


##########################################################
class YearFilter(admin.SimpleListFilter):
    title = 'Год'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        current_year = timezone.now().year
        return [(year, year) for year in range(current_year - 1, current_year + 1)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__year=self.value())
        return queryset


##########################################################
class MonthFilter(admin.SimpleListFilter):
    title = 'Месяц'
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        months = [
            (1, 'Январь'),
            (2, 'Февраль'),
            (3, 'Март'),
            (4, 'Апрель'),
            (5, 'Май'),
            (6, 'Июнь'),
            (7, 'Июль'),
            (8, 'Август'),
            (9, 'Сентябрь'),
            (10, 'Октябрь'),
            (11, 'Ноябрь'),
            (12, 'Декабрь'),
        ]
        return months

    def queryset(self, request, queryset):
        if self.value():
            year = request.GET.get('year')  # Получаем выбранный год
            if year:
                return queryset.filter(date__month=self.value(), date__year=year)
        return queryset


##########################################################
##########################################################
class DocForm(forms.ModelForm):
    content = forms.CharField(label='Описание', widget=CKEditorUploadingWidget())

    class Meta:
        model = Doc
        fields = '__all__'


class DocAdmin(admin.ModelAdmin):
    list_display = ('title', 'created')
    form = DocForm
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('views', 'publish',)


##########################################################
class KatAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}


##########################################################
class InfoForm(forms.ModelForm):
    content = forms.CharField(label='Информация', widget=CKEditorUploadingWidget())

    class Meta:
        model = Info
        fields = '__all__'


class InfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    form = InfoForm
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('views', 'publish',)


##########################################################
class NewsForm(forms.ModelForm):
    body = forms.CharField(label='Текст новости', widget=CKEditorUploadingWidget())

    class Meta:
        model = News
        fields = '__all__'


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_html_photo', 'slug')
    form = NewsForm
    prepopulated_fields = {"slug": ("title",)}
    fields = ('title', 'slug', 'get_html_photo', 'img', 'body', 'file', 'publish', 'views')
    readonly_fields = ('views', 'publish', 'get_html_photo')

    def get_html_photo(self, object):
        if object.img:
            return mark_safe(f"<img src='{object.img.url}' width='100px'>")

    get_html_photo.short_description = "Фото"


##########################################################
class CardForm(forms.ModelForm):
    description = forms.CharField(label='Описание', widget=CKEditorUploadingWidget())

    class Meta:
        model = Card
        fields = '__all__'


class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'home')
    form = CardForm
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('home',)

    def save_model(self, request, obj, form, change):
        # Проверяем, есть ли значение в сессии
        choice_home = request.session.get('choice_home', '7')  # '7' — значение по умолчанию
        obj.home = choice_home  # Устанавливаем значение поля home
        super().save_model(request, obj, form, change)


############################################################

class MeterDevAdmin(admin.ModelAdmin):
    actions = ["export_to_csv"]
    list_display = ('kv', 'name', 'number', 'data_pov_next', 'date_akt', 'type', 'home')
    search_fields = ['data_pov_next']
    list_filter = (MonthDevFilter,)
    ordering = ['kv']

    class Meta:
        model = MeterDev
        fields = ('kv', 'name', 'number', 'data_pov_next', ' plomba', 'amg', 'pokazaniya', 'date_akt', 'type', 'home')

    # даем django(urlpatterns) знать
    # о существовании страницы с формой
    # иначе будет ошибка
    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('csv-upload/', self.upload_csv))
        return urls

    # если пользователь открыл url 'csv-upload/'
    # то он выполнит этот метод
    # который работает с формой
    def upload_csv(self, request):
        if request.method == "POST":
            form = MeterImportForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file(request, request.FILES["csv_file"])
                # конец обработки файлы
                # перенаправляем пользователя на главную страницу
                # с сообщением об успехе
                url = reverse('admin:index')
                messages.success(request, 'Файл успешно импортирован')
                return HttpResponseRedirect(url)
        form = MeterImportForm()
        return render(request, 'admin/csv_import_page.html', {'form': form})

    def export_to_csv(self, request, queryset):
        # Создаем HTTP-ответ с заголовками для CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="MeterDev_export.csv"'

        writer = csv.writer(response)

        # Записываем заголовки
        # writer.writerow(['ID', 'Тип счетчика'])  # Добавьте другие заголовки по необходимости
        writer.writerow(['Кв', 'Наименование ПУ', 'Заводской номер', 'Дата следующей поверки', 'Пломба',
                         'Антимагнитная пломба', 'Начальные показания', 'Дата акта', 'Тип счетчика', 'Дом'])

        for obj in queryset:
            type_display = dict(MeterDev.TYPE_SELECT).get(obj.type, obj.type)  # Получаем отображаемое значение
            writer.writerow([obj.kv, obj.name, obj.number, obj.data_pov_next,
                             obj.plomba, obj.amg, obj.pokazaniya,
                             obj.date_akt, type_display, obj.home])
        return response

    export_to_csv.short_description = "Экспорт в CSV"


###########################################################
class PokazaniyaAdmin(ImportExportModelAdmin, ExportActionMixin, admin.ModelAdmin):
    list_display = ('kv', 'hv', 'gv', 'e', 'date',)
    search_fields = ['date']
    ordering = ['kv']
    list_filter = (YearFilter, MonthFilter, 'home')
    save_on_top = True

    class Meta:
        model = Pokazaniya
        fields = ('kv', 'hv', 'gv', 'e', 'date', 'home')


###########################################################

class PokazaniyaUserAdmin(admin.ModelAdmin):
    actions = ["export_to_csv"]
    list_display = ('home', 'kv', 'hv', 'gv', 'e', 'date', 'ls')
    search_fields = ['date']
    ordering = ['kv']
    list_filter = (YearFilter, MonthFilter, 'home')
    save_on_top = True
    readonly_fields = ('home',)

    class Meta:
        model = PokazaniyaUser
        fields = ('home', 'kv', 'hv', 'gv', 'e', 'date', 'ls')

    def export_to_csv(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "Нет данных для экспорта.", level='warning')
            return HttpResponse(status=204)  # No content

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="PokazaniyaUser_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Кв', 'ХВС', 'ГВС', 'ЭЛ-ВО', 'Дата', 'Дом', 'Л.С'])

        # Словарь для хранения последних записей по уникальным kv
        unique_records = {}

        for obj in queryset:
            key = obj.kv  # Используем только kv как уникальный ключ
            # Сохраняем только последние записи по уникальному ключу
            if key not in unique_records or obj.date > unique_records[key].date:
                unique_records[key] = obj

        # Записываем только последние записи по уникальным kv
        for obj in unique_records.values():
            writer.writerow([obj.kv, obj.hv, obj.gv, obj.e, obj.date.strftime('%d-%m-%Y'), obj.home, obj.ls])

        return response

    export_to_csv.short_description = "Экспорт в CSV"


###########################################################

class ZayavkiAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created')

    class Meta:
        model = Zayavki
        fields = '__all__'


###########################################################
def uploaded_file(request, file):
    # обработка csv файла
    with open(f"{settings.MEDIA_ROOT}/uploads/{file}", "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    # обработка csv файла
    with open(f"{settings.MEDIA_ROOT}/uploads/{file}", 'r', encoding='utf-8') as csv_file:
        rows = csv.reader(csv_file, delimiter=',')
        if next(rows) != ['Кв', 'Наименование ПУ', 'Заводской номер', 'Дата следующей поверки', 'Пломба',
                          'Антимагнитная пломба', 'Начальные показания', 'Дата акта', 'Тип счетчика', 'Дом']:
            # обновляем страницу пользователя
            # с информацией о какой-то ошибке
            messages.warning(request, 'Неверные заголовки у файла')
            return HttpResponseRedirect(request.path_info)

        for row in rows:
            # print(
            #     f"kv={row[0]};name={row[1]};number={row[2]};data_pov_next={row[3]};plomba={row[4]};amg={row[5]};"
            #     f"pokazaniya={row[6]};date_akt={row[7]};type={row[8]};")
            #
            if row[8] == 'ХВС':
                t = 'hv'
            elif row[8] == 'ГВС':
                t = 'gv'
            elif row[8] == 'ЭЛ-ВО':
                t = 'e'
            try:
                m = MeterDev.objects.filter(kv=row[0], type=t, home=row[9])
                if m:
                    m.update(kv=row[0], name=row[1], number=row[2], data_pov_next=row[3], plomba=row[4], amg=row[5],
                             pokazaniya=row[6], date_akt=row[7], type=t, home=row[9])
                else:
                    MeterDev.objects.create(kv=row[0], name=row[1], number=row[2], data_pov_next=row[3], plomba=row[4],
                                            amg=row[5],
                                            pokazaniya=row[6], date_akt=row[7], type=t, home=row[9])

            except ValidationError as e:
                url = reverse('admin:index')
                messages.error(request, 'Ошибка, неверный формат файла')
                # удаляем файл
                os.remove(f"{settings.MEDIA_ROOT}/uploads/{file}")
                return HttpResponseRedirect(url)
    # удаляем файл
    os.remove(f"{settings.MEDIA_ROOT}/uploads/{file}")


###########################################################
class MyAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        # Получаем значение из сессии
        choice_home = request.session.get('choice_home', '7')  # '7' — значение по умолчанию
        # Изменяем заголовок админ-панели
        self.site_header = f"Администрирование (ТСН «ЗВЕЗДНЫЙ-{choice_home}»)"

        extra_context = extra_context or {}
        extra_context['choice_home'] = choice_home
        return super().index(request, extra_context=extra_context)


###########################################################

###########################################################
admin_site = MyAdminSite(name='myadmin')
admin_site.register(Doc, DocAdmin)
admin_site.register(KatDoc, KatAdmin)
admin_site.register(Info, InfoAdmin)
admin_site.register(Card, CardAdmin)
admin_site.register(News, NewsAdmin)
admin_site.register(UserMessage)
admin_site.register(Pokazaniya, PokazaniyaAdmin)
admin_site.register(Zayavki, ZayavkiAdmin)
admin_site.register(PokazaniyaUser, PokazaniyaUserAdmin)
admin_site.register(MeterDev, MeterDevAdmin)
# app = bot
admin_site.register(UsersBot, UsersBotAdmin)
# app = users
admin_site.register(User, UserAdmin)
admin_site.register(Receipts, ReceiptsAdmin)

# admin.site.register(Doc, DocAdmin)
# admin.site.register(KatDoc, KatAdmin)
# admin.site.register(Info, InfoAdmin)
# admin.site.register(Card, CardAdmin)
# admin.site.register(News, NewsAdmin)
# admin.site.register(UserMessage)
# admin.site.register(Pokazaniya, PokazaniyaAdmin)
# admin.site.register(Zayavki, ZayavkiAdmin)
# admin.site.register(PokazaniyaUser, PokazaniyaUserAdmin)
# admin.site.register(MeterDev, MeterDevAdmin)
