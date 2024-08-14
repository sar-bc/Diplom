from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta
from .models import *
from django.contrib.auth.models import User
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from django.utils.html import format_html

##########################################################
admin.site.site_title = 'Админ-панель ТСН'
admin.site.site_header = 'Админ-панель ТСН'


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
    list_display = ('title', 'slug')
    form = CardForm
    prepopulated_fields = {"slug": ("title",)}


###########################################################
# class ProfileAdmin(ImportExportModelAdmin, admin.ModelAdmin):
#     list_display = ('kv','ls','fio','sq','email','phone')
#     readonly_fields = ('created', 'updated')
#     class Meta:
#         model = Profile
#         fields = ('kv','ls', 'address', 'fio', 'sq')
###########################################################
# class UserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
#     search_fields = ["username"]
#     list_editable = ('is_active',)
#     list_display = ('username', 'is_active')

# class Meta:
#     mosel = User
#     fields = ('username', 'password')
###########################################################
class MeterDevAdmin(ImportExportModelAdmin, ExportActionMixin, admin.ModelAdmin):
    list_display = ('kv', 'name', 'number', 'data_pov_next', 'date_akt', 'type')
    search_fields = ['data_pov_next']
    # list_filter = ['data_pov_next']
    list_filter = (MonthDevFilter,)
    ordering = ['kv']

    class Meta:
        model = MeterDev
        fields = ('kv', 'name', 'number', 'data_pov_next', ' plomba', 'amg', 'pokazaniya', 'date_akt', 'type')


###########################################################
class PokazaniyaAdmin(ImportExportModelAdmin, ExportActionMixin, admin.ModelAdmin):
    list_display = ('kv', 'hv', 'gv', 'e', 'date',)
    search_fields = ['date']
    ordering = ['kv']
    # list_filter = ['date']
    list_filter = (YearFilter, MonthFilter)
    save_on_top = True

    class Meta:
        model = Pokazaniya
        fields = ('kv', 'hv', 'gv', 'e', 'date',)


###########################################################
@admin.register(PokazaniyaUser)
class PokazaniyaUserAdmin(ImportExportModelAdmin, ExportActionMixin, admin.ModelAdmin):
    list_display = ('kv', 'hv', 'gv', 'e', 'date',)
    search_fields = ['date']
    ordering = ['kv']
    # list_filter = ['date']
    list_filter = (YearFilter, MonthFilter)
    save_on_top = True

    class Meta:
        model = PokazaniyaUser
        fields = ('kv', 'hv', 'gv', 'e', 'date',)


###########################################################
@admin.register(Zayavki)
class ZayavkiAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created')

    class Meta:
        model = Zayavki
        fields = '__all__'


###########################################################


###########################################################
admin.site.register(Doc, DocAdmin)
admin.site.register(KatDoc, KatAdmin)
admin.site.register(Info, InfoAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(UserMessage)
admin.site.register(MeterDev, MeterDevAdmin)
admin.site.register(Pokazaniya, PokazaniyaAdmin)
