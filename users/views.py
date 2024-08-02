from audioop import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from users.forms import *
from main.forms import PokazaniyaForm, ZayavkaForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
import csv
from django.contrib.auth import get_user_model
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import re
from users.utils import check_email, send_email_for_verify
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.exceptions import ValidationError
from main.models import MeterDev, Pokazaniya, PokazaniyaUser, Zayavki
from django.db import IntegrityError
import datetime
from .models import Receipts

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
        'form': form,
    }
    return render(request, 'users/login.html', context)


@login_required
def profile(request):
    data_user = get_object_or_404(User, ls=request.user.username)
    form = EditProfile(data=data_user)  # (fio=data_user.fio)
    form_phone = EditPhone(data=data_user)
    form_email = EditEmail(data=data_user)
    form_password = ChangeForm(user=request.user)

    context = {
        'title': 'Профиль пользователя',
        'data_user': data_user,
        'form': form,
        'form_phone': form_phone,
        'form_email': form_email,
        'form_password': form_password
    }
    return render(request, 'users/profile.html', context)



@login_required()  # login_url="/users/login/"
def lk_user(request):
    zayavki = Zayavki.objects.filter(user_id=request.user.id)
    data_user = get_object_or_404(User, ls=request.user.username)
    form_pokaz = PokazaniyaForm(data=data_user)
    form_zayavka = ZayavkaForm(data=data_user)
    form_receipt = Lk_receiptForm()
    device = MeterDev.objects.filter(kv=request.user.kv).all()
    pokaz_dev = list(Pokazaniya.objects.filter(kv=request.user.kv).order_by("-date").values())
    p = []
    if pokaz_dev:
        p = pokaz_dev[0]

    context = {
        'title': "Личный кабинет",  # request.user.username,
        'data_user': data_user,
        'device': device,
        'zayavki': zayavki,
        'pokaz_dev': p,
        'form_pokaz': form_pokaz,
        'form_zayavka': form_zayavka,
        'form_receipt': form_receipt,
    }
    return render(request, 'users/lk.html', context)



###############################################################
def show_zayavka(request, id):
    zayavka = Zayavki.objects.filter(user_id=request.user.id).get(id=id)
    context = {
        'title': "Личный кабинет",  # request.user.username,
        'zayavka': zayavka
    }
    return render(request, 'users/show_zayavka.html', context)


###############################################################
class ChangePasswordAjax(View):
    model = User

    def post(self, request):
        form_password = PasswordChangeForm(user=request.user, data=request.POST)
        if form_password.is_valid():
            form_password.save()
            return JsonResponse(data={'status': 201, 'response': "Успешно, войдите заново!"}, status=200)

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
                send_email_for_verify(request, request.user, request.POST.get('email'))
                return JsonResponse(data={'status': 201, 'response': "Подтверждение email на почте"}, status=200)

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
    if request.method == "POST":
        logout(request)
        return redirect('home')


#########################################################
@login_required
def deletezayavka(request, pk):
    zayavka = get_object_or_404(Zayavki, pk=pk, user=request.user)
    if request.method == "POST":
        zayavka.delete()
        return redirect('users:lk_user')


#########################################################
class ZayavkaWriteAjax(View):
    def post(self, request):
        reg = "^[+]{1}7 [(]{1}[0-9]{3}[)]{1} [0-9]{3} [0-9]{4}$"
        check_num = re.search(reg, request.POST.get('phone'))
        if check_num is None:
            return JsonResponse(data={'status': 400, 'error': "Проверьте правильность номера"}, status=200)
        if len(request.POST.get('description')) < 5:
            return JsonResponse(data={'status': 400, 'error': 'Поле описание менее 5 символов'}, status=200)
        try:
            Zayavki.objects.create(user=request.user, description=request.POST.get('description'),
                                   phone=request.POST.get('phone'))
            # send email admin
            mess = ("Новое сообщение от " + request.user.username + "; Тел: " + request.POST.get('phone') +
                    "; Сообщение: " + request.POST.get('description'))
            send_mail('Уведомление с сайта ТСН', mess, settings.EMAIL_HOST_USER,
                      [settings.EMAIL_FROM_ADMIN, settings.EMAIL_FROM_CLIENT], fail_silently=False, )
        except IntegrityError:
            return JsonResponse(data={'status': 400, 'error': "Ошибка"}, status=200)
        return JsonResponse(data={'status': 201, 'response': "Заявка успешно отправлена"}, status=200)


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

        now = datetime.datetime.now()
        if PokazaniyaUser.objects.filter(date__month=now.month):
            return JsonResponse(data={'status': 400, 'error': "В этом месяце вы уже передавали показания"}, status=200)
        try:
            PokazaniyaUser.objects.create(
                kv=request.POST.get('kv'),
                hv=request.POST.get('hv'),
                gv=request.POST.get('gv'),
                e=request.POST.get('e')
            )
            return JsonResponse(data={'status': 201, 'response': "Показания добавлены"}, status=200)
        except ValueError:
            return JsonResponse(data={'status': 400, 'error': "Ошибка"}, status=200)

        # return JsonResponse(data={'status': 201, 'response': "Показания добавлены"}, status=200)
        # return JsonResponse(data={'status': 400, 'error': "Ошибка"}, status=200)


#########################################################
def receipt(request):
    try:
        kvitan = Receipts.objects.filter(date__month=request.POST['month'], date__year=request.POST[
            'year']).get(ls=request.user.ls)
    except Receipts.DoesNotExist:
        kvitan = None

    context = {
        'title': "Платежный документ",  # request.user.username,
        'kvitan': kvitan,

    }
    return render(request, 'users/receipt.html', context)
#########################################################
