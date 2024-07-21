from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from django.core.exceptions import ValidationError
# обслуживание импорта
import csv
from .forms import UserImportForm, ReceiptsImportForm, UserCreationForm
from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
import os
from django import forms
from django.contrib.auth.admin import UserAdmin

User = get_user_model()
from .models import Receipts
import PyPDF2


# https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#a-full-example


class UserAdmin(UserAdmin):  # admin.ModelAdmin
    add_form = UserCreationForm  # CustomUserCreationForm
    search_fields = ["username"]
    # list_editable = ('is_active',)
    list_display = ('username', 'kv')
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Персональная информация"), {"fields": ("fio", "address", "email", "phone", "ls", "kv", "sq")}),
        (
            ("Разрешения"), {"fields": ("is_active", "is_staff", "is_superuser",)}
        ),
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'ls', 'kv', 'fio', 'address', 'sq', 'phone')

    def __str__(self):
        return str(self.username)

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
            form = UserImportForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file(request, request.FILES["csv_file"])
                # конец обработки файлы
                # перенаправляем пользователя на главную страницу
                # с сообщением об успехе
                url = reverse('admin:index')
                messages.success(request, 'Файл успешно импортирован')
                return HttpResponseRedirect(url)
        form = UserImportForm()
        return render(request, 'admin/csv_import_page.html', {'form': form})


# admin.site.unregister(User)
admin.site.register(User, UserAdmin)


def uploaded_file(request, file):
    # обработка csv файла
    with open(f"{settings.MEDIA_ROOT}/uploads/{file}", "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    # обработка csv файла
    with open(f"{settings.MEDIA_ROOT}/uploads/{file}", 'r') as csv_file:
        rows = csv.reader(csv_file, delimiter=';')
        if next(rows) != ['username', 'password', 'kv', 'ls', 'address', 'fio', 'sq', 'phone']:
            # обновляем страницу пользователя
            # с информацией о какой-то ошибке
            messages.warning(request, 'Неверные заголовки у файла')
            return HttpResponseRedirect(request.path_info)
        for row in rows:
            # ВСТАВИТЬ ПРОВЕРКУ НА ПРАВИЛЬНОМТЬ ДАННЫХ
            # print(f"username={row[0]};password={row[1]};kv={row[2]};ls={row[3]};address={row[4]};fio={row[5]};sq={row[6]};phone={row[7]};")
            # добавляем данные в базу
            try:
                username, password, kv, ls, address, fio, sq, phone = row
                if User.objects.filter(username=username):
                    print("Такой user есть", username)
                    continue
                else:
                    User.objects.create_user(username=username, password=password, kv=kv, ls=ls, address=address,
                                             fio=fio, sq=sq, phone=phone)
                    print("Saved", username)
            except ValidationError as e:
                url = reverse('admin:index')
                messages.error(request, 'Ошибка, неверный формат файла')
                # удаляем файл
                os.remove(f"{settings.MEDIA_ROOT}/uploads/{file}")
                return HttpResponseRedirect(url)
        # удаляем файл
        os.remove(f"{settings.MEDIA_ROOT}/uploads/{file}")


#####################################################################################
@admin.register(Receipts)
class ReceiptsAdmin(admin.ModelAdmin):
    list_display = ('ls', 'date', 'file')
    search_fields = ["ls", "date"]
    list_filter = ['date']

    class Meta:
        model = Receipts

    def __str__(self):
        return str(self.ls)

        # даем django(urlpatterns) знать
        # о существовании страницы с формой
        # иначе будет ошибка

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('pdf-upload/', self.upload_pdf))
        return urls

    # если пользователь открыл url 'pdf-upload/'
    # то он выполнит этот метод
    # который работает с формой
    def upload_pdf(self, request):
        if request.method == "POST":
            form = ReceiptsImportForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file_pdf(request, request.FILES["pdf_file"])
                # конец обработки файлы
                # перенаправляем пользователя на главную страницу
                # с сообщением об успехе
                url = reverse('admin:index')
                # messages.success(request, 'Файл успешно импортирован')
                return HttpResponseRedirect(url)
        form = ReceiptsImportForm()
        return render(request, 'admin/pdf_import_page.html', {'form': form})


######################################################################################
def uploaded_file_pdf(request, file):
    year = request.POST.get('date')[:4]
    month = request.POST.get('date')[5:7]
    # print(f"file:{file}")
    if str(file).endswith('.pdf'):

        # обработка pdf файла загрузка в папку uploads
        with open(f"{settings.MEDIA_ROOT}/uploads/{file}", "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Открываем PDF файл
        with open(f"{settings.MEDIA_ROOT}/uploads/{file}", 'rb') as file:
            # Создаем объект PDF Reader
            pdf_reader = PyPDF2.PdfReader(file)
            # Получаем количество страниц в PDF файле
            num_pages = len(pdf_reader.pages)
            # num_kv = Receipts.objects.filter(kv__gt=0).count()
            # print(f"num_kv:{num_kv}")
            ls = []
            kv = User.objects.filter(kv__gt=0)
            for ls_lst in kv:
                ls.append(ls_lst.ls)
            if len(ls) == num_pages:
                # кол-во лицевых совподает с кол-вом страниц в файле pdf
                if not os.path.exists(f"{settings.MEDIA_ROOT}/receipts"):
                    os.makedirs(f"{settings.MEDIA_ROOT}/receipts")
                if not os.path.exists(f"{settings.MEDIA_ROOT}/receipts/{year}"):
                    os.makedirs(f"{settings.MEDIA_ROOT}/receipts/{year}")
                if not os.path.exists(f"{settings.MEDIA_ROOT}/receipts/{year}/{month}"):
                    os.makedirs(f"{settings.MEDIA_ROOT}/receipts/{year}/{month}")

                    # Сохраняем каждую страницу в отдельный файл
                    for page_num in range(num_pages):
                        page = pdf_reader.pages[page_num]
                        with open(f"{settings.MEDIA_ROOT}/receipts/{year}/{month}/{ls[page_num]}_{month}_{year}.pdf",
                                  'wb') as output_file:
                            pdf_writer = PyPDF2.PdfWriter()
                            pdf_writer.add_page(page)
                            pdf_writer.write(output_file)
                            Receipts.objects.create(ls=f'{ls[page_num]}',
                                                    date=f'{year}-{month}-25',
                                                    file=f'receipts/{year}/{month}/{ls[page_num]}_{month}_{year}.pdf')
                messages.success(request, 'Файл успешно импортирован')
            else:
                # print("ОШИБКА! КОЛ-ВО ЛИЦЕВЫХ НЕ СОВПОДАЕТ С КОЛ-ВОМ СТРАНИЦ В ФАЙЛЕ PDF")

                messages.error(request, 'ОШИБКА! КОЛ-ВО ЛИЦЕВЫХ НЕ СОВПОДАЕТ С КОЛ-ВОМ СТРАНИЦ В ФАЙЛЕ PDF')

            # удаляем файл
            os.remove(f"{file.name}")

    else:
        messages.error(request, "Ошибка формата файла")
