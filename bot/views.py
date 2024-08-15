#  https://habr.com/ru/sandbox/186542/ (Создание телеграм бота на Django + pyTelegramBotApi)
from django.shortcuts import HttpResponse
import telebot
from telebot import types  # для указание типов
from django.conf import settings
from .models import UsersBot
from main.models import MeterDev, Pokazaniya, PokazaniyaUser
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from datetime import date

User = get_user_model()

bot = telebot.TeleBot(settings.BOT_TOKEN)

last_message_id = None
last_message_id_lst = []
user_id = None
step = 0  # шаг 0 (принимаем лицевой или квартиру), 1,2,3 (принимаем показания ХВС,ГВС.ЭЛ-ВО)
type_dev = ['-', 'hv', 'gv', 'e']
kv = 0
ls_glob = 0
##############################################
res_ls = int()
res_kv = int()


##############################################


@csrf_exempt
def index(request):
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])
    else:
        bot.remove_webhook()
        bot.set_webhook(f'{settings.SERVER_BOT}/bot/')
    return HttpResponse(f'<h1>Ты подключился!</h1>:{bot.get_webhook_info()}')


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    global last_message_id
    global last_message_id_lst
    global user_id
    global step
    step = 0
    user_id = message.from_user.id
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id_lst:
        for lst in last_message_id_lst:
            try:
                bot.delete_message(message.chat.id, lst)
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")
        last_message_id_lst.clear()
    # выводитм список лицевых
    call_all_ls_f(message)


########
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # Извлекаем данные из callback_data
    data = call.data.split(':')
    action = data[0]
    global last_message_id
    global last_message_id_lst
    global user_id
    global type_dev
    global step
    global kv
    global ls_glob
    step = 0
    # Удаляем предыдущее сообщение, если оно существует
    delete_messages(call.message)

    if action == 'call_add_ls':
        # добавить лицевой счет
        call_add_ls_f(call)

    elif action == 'call_show_ls':
        # показать лицевой счет №
        ls = data[1]
        ls_glob = ls
        call_show_ls_f(call.message)

    elif action == 'call_all_ls':
        # показать все лицевые счета
        call_all_ls_f(call.message)

    elif action == 'call_add_pokazaniya':
        # добавить показания
        pu_kv = data[1]
        kv = pu_kv
        pu_type = data[2]
        pu_type_display = data[3]
        ls = data[4]
        call_add_pokazaniya_f(call.message, pu_type, pu_type_display, ls)

    elif action == 'call_del_ls':
        # запрос на удаление лицевого счета
        ls = data[1]
        ls_glob = ls
        call_del_ls_f(call.message)

    elif action == 'call_del_ls_yes':
        # удаление лицевого счета
        ls = data[1]
        ls_glob = ls
        call_del_ls_yes_f(call.message)


##############################################
# обработка входящего текста
@bot.message_handler(content_types=['text'])
def func(message):
    global res_ls
    global res_kv
    global step
    if step == 0:
        if len(message.text) == 8:
            try:
                res_ls = int(message.text)
                bot.send_message(message.chat.id,
                                 text="Очень хорошо! Теперь введите номер квартиры (не более 3 символов).")
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Вы ввели некорректное значение! Введите номер лицевого счета еще раз")
        elif 1 <= len(message.text) <= 3:
            try:
                res_kv = int(message.text)
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Вы ввели некорректное значение! Введите номер квартиры еще раз")

            if res_ls and res_kv:
                bot.send_message(message.chat.id, text="Подождите, идёт поиск и привязка лицевого счета..")
                u = User.objects.filter(ls=res_ls, kv=res_kv)
                if u:
                    # добавляем данные телеграм user и лицевой
                    UsersBot.objects.create(user_id=message.from_user.id, username=message.from_user.username,
                                            ls=res_ls,
                                            kv=res_kv)
                    bot.send_message(message.chat.id, text=f"Лицевой счет №{res_ls} успешно добавлен.")
                    call_all_ls_f(message)
                else:
                    bot.send_message(message.chat.id,
                                     text="Не удалось найти указанный лицевой счет! Обратитесь в офис ТСН")
        else:
            bot.send_message(message.chat.id,
                             text="Вы ввели некорректное значение! Введите номер лицевого счета еще раз")
    elif step == 1:
        if 1 <= len(message.text) <= 8:  # длина показаний
            try:
                val = int(message.text)
                bot.send_message(message.chat.id,
                                 text=f"Введено показание:{val}... ожидайте")
                try:
                    req = PokazaniyaUser.objects.filter(date=date.today(), kv=kv)
                    if req:
                        req.update(hv=val)
                    else:
                        PokazaniyaUser.objects.create(kv=kv, hv=val)
                except IntegrityError:
                    print("Ошибка")
                bot.send_message(message.chat.id,
                                 text=f"Показания приняты успешно!")
                call_show_ls_f(message)
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Введено некорректное число. Попробуйте еще раз:")
        else:
            bot.send_message(message.chat.id,
                             text="Количество символов превышает 8. Попробуйте еще раз:")
    elif step == 2:
        if 1 <= len(message.text) <= 8:  # длина показаний
            try:
                val = int(message.text)
                bot.send_message(message.chat.id,
                                 text=f"Введено показание:{val}... ожидайте")
                try:
                    req = PokazaniyaUser.objects.filter(date=date.today(), kv=kv)
                    if req:
                        req.update(gv=val)
                    else:
                        PokazaniyaUser.objects.create(kv=kv, gv=val)
                except IntegrityError:
                    print("Ошибка")
                bot.send_message(message.chat.id,
                                 text=f"Показания приняты успешно!")
                call_show_ls_f(message)
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Введено некорректное число. Попробуйте еще раз:")
        else:
            bot.send_message(message.chat.id,
                             text="Количество символов превышает 8. Попробуйте еще раз:")
    elif step == 3:
        if 1 <= len(message.text) <= 8:  # длина показаний
            try:
                val = int(message.text)
                bot.send_message(message.chat.id,
                                 text=f"Введено показание:{val}... ожидайте")
                try:
                    req = PokazaniyaUser.objects.filter(date=date.today(), kv=kv)
                    if req:
                        req.update(e=val)
                    else:
                        PokazaniyaUser.objects.create(kv=kv, e=val)
                except IntegrityError:
                    print("Ошибка")
                bot.send_message(message.chat.id,
                                 text=f"Показания приняты успешно!")
                call_show_ls_f(message)
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Введено некорректное число. Попробуйте еще раз:")
        else:
            bot.send_message(message.chat.id,
                             text="Количество символов превышает 8. Попробуйте еще раз:")


##############################################
#  function
# функция показать все лицевые
def call_all_ls_f(obj):
    user_bot = UsersBot.objects.filter(user_id=user_id)
    # print(f'user_bot:{user_bot}')
    keyboard = types.InlineKeyboardMarkup()
    if user_bot:
        # id есть в базе
        for u_b in user_bot:
            # print(f'u_b:{u_b.ls}')
            btn_show_ls = types.InlineKeyboardButton(f"🏠 {u_b.ls}-{u_b.kv}", callback_data=f'call_show_ls:{u_b.ls}')
            keyboard.add(btn_show_ls)

    btn_add_ls = types.InlineKeyboardButton("🔍 Добавить лицевой счет", callback_data='call_add_ls')

    keyboard.add(btn_add_ls)
    sent_mess = bot.send_message(obj.chat.id, f'Выберите Лицевой счёт из списка, либо добавьте новый',
                                 reply_markup=keyboard)
    last_message_id_lst.append(sent_mess.message_id)


# функция удаления сообщений
def delete_messages(obj):
    if last_message_id_lst:
        for lst in last_message_id_lst:
            try:
                bot.delete_message(obj.chat.id, lst)
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")
        last_message_id_lst.clear()


# функция добавления лицевого счета
def call_add_ls_f(call):
    bot.send_message(call.message.chat.id, f'Введите номер лицевого счета (только цифры, не более 8 цифр).')


# функция показать лицевой
def call_show_ls_f(obj):
    bot.send_message(obj.chat.id, f"Получение списка счётчиков... ожидайте.")
    # sent_mess = bot.send_message(obj.chat.id, f"Получение списка счётчиков... ожидайте.")
    # last_message_id_lst.append(sent_mess.message_id)
    try:
        user = User.objects.get(ls=ls_glob)
        mes = (f"Лицевой счет № {ls_glob}\n"
               f"Адрес: {user.address}\n")

        keyboard = types.InlineKeyboardMarkup()
        # цикл для счетчиков
        dev = MeterDev.objects.filter(kv=user.kv)
        if dev:
            mes += f"Выберите прибор учета из списка"
            for pu in dev:
                type_display = dict(MeterDev.TYPE_SELECT).get(pu.type, 'Неизвестный тип')
                btn_meter = types.InlineKeyboardButton(f"{type_display}, {pu.number}",
                                                       callback_data=f'call_add_pokazaniya:{user.kv}:'
                                                                     f'{pu.type}:{type_display}:{ls_glob}')
                keyboard.add(btn_meter)
        else:
            mes += f"⛔ Приборы учета не добавлены, обратитесь в офис ТСН"

        btn_back = types.InlineKeyboardButton("⬅️ Возврат в начало", callback_data=f'call_all_ls')
        btn_del = types.InlineKeyboardButton("❌ Отвязать счет", callback_data=f'call_del_ls:{ls_glob}')
        keyboard.add(btn_back, btn_del)
        sent_mess = bot.send_message(obj.chat.id, mes, reply_markup=keyboard)
        last_message_id_lst.append(sent_mess.message_id)

    except User.DoesNotExist:
        mes = f"Лицевой счет № {ls_glob} не найден!"
        bot.send_message(obj.chat.id, mes)


# функция приема показаний
def call_add_pokazaniya_f(obj, pu_type, pu_type_display, ls):
    global step
    if pu_type == 'hv':
        step = 1
    elif pu_type == 'gv':
        step = 2
    elif pu_type == 'e':
        step = 3

    p = []
    try:
        num_pu = MeterDev.objects.get(kv=kv, type=pu_type)
    except MeterDev.DoesNotExist:
        bot.send_message(obj.chat.id, f'Прибор не найден')
    try:
        pokaz_dev = list(Pokazaniya.objects.filter(kv=kv).order_by("-date").values())
        if pokaz_dev:
            p = pokaz_dev[0]
        # print(p['date'])
    except Pokazaniya.DoesNotExist:
        bot.send_message(obj.chat.id, f'Показания не найдены')
    keyboard = types.InlineKeyboardMarkup()
    date_mess = p['date'].strftime('%d.%m.%Y')
    mes = (f'Прибор учета:{pu_type_display},{num_pu.number}\n'
           f'Предыдущие:{p[pu_type]} ({date_mess})\n'
           f'Введите текущее показание ниже :')
    btn_back = types.InlineKeyboardButton("⬅️ Возврат к списку счетчиков", callback_data=f'call_show_ls:{ls}')
    keyboard.add(btn_back)
    sent_mess = bot.send_message(obj.chat.id, mes, reply_markup=keyboard)
    last_message_id_lst.append(sent_mess.message_id)


# функция запроса удаления лицевого
def call_del_ls_f(obj):
    try:
        user = User.objects.get(ls=ls_glob)
    except User.DoesNotExist:
        mes = f"Лицевой счет № {ls_glob} не найден!"
        bot.send_message(obj.chat.id, mes)

    keyboard = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("Да", callback_data=f'call_del_ls_yes:{ls_glob}')
    btn_no = types.InlineKeyboardButton("Нет", callback_data=f'call_show_ls:{ls_glob}')
    keyboard.add(btn_yes, btn_no)
    sent_mess = bot.send_message(obj.chat.id, f'Вы точно хотите отвязать Лицевой счет?\n'
                                              f'Счет № {ls_glob}\n'
                                              f'Адрес: {user.address}',
                                 reply_markup=keyboard)
    last_message_id_lst.append(sent_mess.message_id)


# функция удаления лицевого
def call_del_ls_yes_f(obj):
    try:
        u = UsersBot.objects.get(ls=ls_glob)
        u.delete()
        bot.send_message(obj.chat.id, f'Лицевой счет №{ls_glob} успешно отвязан!')
        call_all_ls_f(obj)
        # keyboard = types.InlineKeyboardMarkup()
        # btn_add_ls = types.InlineKeyboardButton("🔍 Добавить лицевой счет", callback_data='call_add_ls')
        # keyboard.add(btn_add_ls)
        # sent_mess = bot.send_message(obj.chat.id, f'У вас нет добавленных лицевых счетов',
        #                              reply_markup=keyboard)
        # last_message_id_lst.append(sent_mess.message_id)
    except UsersBot.DoesNotExist:
        mes = f"Лицевой счет № {ls_glob} не найден!"
        bot.send_message(obj.chat.id, mes)
