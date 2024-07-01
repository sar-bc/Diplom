from audioop import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from users.forms import *
from main.forms import PokazaniyaForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from main.utils import infos, kat_doc, year
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
import csv
from django.contrib.auth import get_user_model
from django.views import View
from django.conf import settings
from django.http import JsonResponse
import re
from users.utils import check_email, send_email_for_verify
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.exceptions import ValidationError
from main.models import MeterDev, Pokazaniya

import datetime

User = get_user_model()


# class LoginUser(LoginView):
#     form_class = AuthenticationForm
#     template_name = 'users/login.html'
#     extra_context = {'title': "Авторизация"}

def login_user(request):
    if request.method == "POST":
        form = LoginUserForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('users:lk_user')
    else:
        form = LoginUserForm()

    context = {
        'title': 'Вход в личный кабинет',
        'year': year,
        'form': form,
        'infos': infos,
        'kat_doc': kat_doc,
    }
    return render(request, 'users/login.html', context=context)


@login_required
def profile(request):
    data_user = get_object_or_404(User, ls=request.user.username)
    form = EditProfile(data=data_user)  # (fio=data_user.fio)
    form_phone = EditPhone(data=data_user)
    form_email = EditEmail(data=data_user)
    form_password = ChangeForm(user=request.user)

    context = {
        'title': 'Профиль пользователя',
        'year': year,
        'infos': infos,
        'kat_doc': kat_doc,
        'data_user': data_user,
        'form': form,
        'form_phone': form_phone,
        'form_email': form_email,
        'form_password': form_password
    }
    return render(request, 'users/profile.html', context=context)
    # return HttpResponse(f"Профиль")


@login_required()  # login_url="/users/login/"
def lk_user(request):
    data_user = get_object_or_404(User, ls=request.user.username)
    form_pokaz = PokazaniyaForm(data=data_user)
    device = MeterDev.objects.filter(kv=request.user.kv).all()
    pokaz_dev = list(Pokazaniya.objects.filter(kv=request.user.kv).order_by("-date").values())
    p = []
    if pokaz_dev:
        p = pokaz_dev[0]
    # print(f"P:{p}")
    # print(pokaz_dev[0]['hv'])


    context = {
        'title': "Личный кабинет",  # request.user.username,
        'year': year,
        'infos': infos,
        'kat_doc': kat_doc,
        'data_user': data_user,
        'device': device,
        'day_start': settings.DAY_PERIOD[0],
        'day_end': settings.DAY_PERIOD[-1],
        'pokaz_dev': p,
        'form_pokaz': form_pokaz,


    }
    return render(request, 'users/lk.html', context=context)
    # return HttpResponse(f"Личный кабинет")


###############################################################
class ChangePasswordAjax(View):
    model = User

    def post(self, request):
        form_password = PasswordChangeForm(user=request.user, data=request.POST)
        if form_password.is_valid():
            form_password.save()
            return JsonResponse(data={'status': 201, 'response': "Успешно"}, status=200)

        errors = form_password.errors.as_json()
        return JsonResponse(data={'status': 400, 'error': errors}, status=200)


#########################################################
class EditPhoneAjax(View):
    def post(self, request):
        # form_phone = EditPhone(request.POST)
        reg = "^[+]{1}7 [(]{1}[0-9]{3}[)]{1} [0-9]{3} [0-9]{4}$"
        check_num = re.search(reg, request.POST.get('phone'))
        # print(f"EditPhoneAjax:{request.user.username}")
        if check_num:
            User.objects.filter(username=request.user.username).update(phone=request.POST.get('phone'))
            return JsonResponse(data={'status': 201, 'response': "Успешно"}, status=200)

        return JsonResponse(data={'status': 400, 'error': "Проверьте правильность номера"}, status=200)


#########################################################
class EditEmailAjax(View):
    def post(self, request):
        if check_email(request.POST.get('email')):
            # print(f"EditEmail:{request.user.email}")
            if request.POST.get('email') == request.user.email and (request.user.check_email == 1):
                # print("Обновлять email не надо!")
                return JsonResponse(data={'status': 201, 'response': "Успешно"}, status=200)
            else:
                User.objects.filter(username=request.user.username).update(email=request.POST.get('email'),
                                                                           check_email=0)
                # отправка email для проверки
                send_email_for_verify(request, request.user)
                return JsonResponse(data={'status': 201}, status=200)

        return JsonResponse(data={'status': 400, 'error': 'Проверьте правильность email'}, status=200)


###############################################################
class EditRecDocAjax(View):
    def post(self, request):
        print(f"rec_doc:{request.POST.get('rec_doc')}")
        if request.POST.get('rec_doc') and request.user.check_email:
            User.objects.filter(username=request.user.username).update(rec_doc=request.POST.get('rec_doc'))
            return JsonResponse(data={'status': 201, 'response': "Успешно"}, status=200)

        return JsonResponse(data={'status': 400, 'error': "Нет или неподтвержден email"}, status=200)


###############################################################
def logout_user(request):
    logout(request)
    return redirect('home')


#########################################################
def add_user(request):
    # print(settings.BASE_DIR)
    file_path = settings.BASE_DIR / 'uploads/upload_profile1.csv'
    if file_path:
        # print("yes file")
        with open(file_path, 'r', encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                username, password, kv, ls, address, fio, sq = row
                # print("username:",username)
                # print("password:",password)
                # print("kv:",kv)
                # print("ls:",ls)
                # print("address:",address)
                # print("fio:",fio)
                # print("sq:",sq)

                if User.objects.filter(username=username):
                    print("Такой user есть", username)
                    continue
                else:
                    User.objects.create_user(username=username, password=password, kv=kv, ls=ls, address=address,
                                             fio=fio, sq=sq)
                    print("Saved", username)
                    # new_user.save()
    else:
        print("no file")
    return HttpResponse(f"upload")


#########################################################
# def add_pokazaniya(request):
#     # print(settings.BASE_DIR)
#     file_path = settings.BASE_DIR / 'uploads/pokazaniya02.24.csv'
#     if file_path:
#         # print("yes file")
#         with open(file_path, 'r') as file:
#             reader = csv.reader(file, delimiter=';')
#             for row in reader:
#                 kv, hv, gv, e, date = row
#
#                 if Pokazaniya.objects.filter(date=date, kv=kv):
#                     print("Такая запись есть ")
#                     continue
#                 else:
#                     Pokazaniya.objects.create(kv=kv, hv=hv, gv=gv, e=e, date=date)
#
#                     print("Saved", kv)
#                     # new_user.save()
#     else:
#         print("no file")
#     return HttpResponse(f"upload")


#########################################################
class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and token_generator.check_token(user, token):
            user.check_email = True
            user.save()
            # login(request, user)
            return redirect('users:profile')
        return redirect('users:invalid_verify')

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError,
                User.DoesNotExist, ValidationError):
            user = None
        return user
#########################################################
class PokazaniyaWriteAjax(View):
    def post(self, request):
        # print(f"pokazwriteajax:")
        # запрашиваем последние показания
        pokaz_dev = list(Pokazaniya.objects.filter(kv=request.user.kv).order_by("-date").values())
        if pokaz_dev:
            # p = pokaz_dev[0]
            print(f"Последние ХВ:{pokaz_dev[0]['hv']}; ГВ:{pokaz_dev[0]['gv']}; Эл-во:{pokaz_dev[0]['e']}; ")
            print(f"Переданные ХВ:{request.POST.get('hv')}; ГВ:{request.POST.get('gv')}; Эл-во:{request.POST.get('e')};")
        # сравниваем что бы переданные были больше прудидущих


        # return JsonResponse(data={'status': 201, 'response': "Показания добавлены"}, status=200)
        return JsonResponse(data={'status': 400, 'error': "Ошибка"}, status=200)
#########################################################
