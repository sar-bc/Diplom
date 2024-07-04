from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from django.core.exceptions import ValidationError
# обслуживание импорта
import csv
from .forms import UserImportForm
from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
import os
User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["username"]
    list_editable = ('is_active',)
    list_display = ('username', 'is_active')

    class Meta:
        model = User
        fields = ('username', 'password')

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
