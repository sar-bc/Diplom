#  https://habr.com/ru/sandbox/186542/ (Создание телеграм бота на Django + pyTelegramBotApi)
from django.shortcuts import HttpResponse
import telebot
from telebot import types  # для указание типов
from django.conf import settings
from bot.models import UsersBot
from main.models import MeterDev, Pokazaniya, PokazaniyaUser
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from datetime import date

User = get_user_model()

bot = telebot.TeleBot(settings.BOT_TOKEN)


##############################################
# Структура для хранения состояния
class BotState:
    def __init__(self):
        self.last_message_ids = []
        self.user_id = None
        self.step = 0
        self.kv = 0
        self.ls = 0


state = BotState()


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


##############################################
@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    state.user_id = None
    state.step = 10
    state.kv = 0
    state.ls = 0
    # state.user_id = message.from_user.id
    delete_messages(message)
    bot.send_message(message.chat.id, "Добро пожаловать!")
    call_all_ls(message, message.from_user.id)
    # step 0- ожидание лицевого
    # step 1- ожидание показания ХВС
    # step 2- ожидание показания ГВС
    # step 3- ожидание показания ЭЛ-ВО
    # step 4- ожидание квартиры


##############################################
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    action, *data = call.data.split(':')
    # Удаление предыдущих сообщений
    delete_messages(call.message)

    actions = {
        'call_add_ls': call_add_ls,
        'call_show_ls': call_show_ls,
        'call_all_ls': call_all_ls,
        'call_add_pokazaniya': call_add_pokazaniya,
        'call_del_ls': call_del_ls,
        'call_del_ls_yes': call_del_ls_yes,
    }

    # Проверяем, есть ли действие в нашем словаре
    if action in actions:
        actions[action](call.message, *data)


##############################################
# FUNCTION
#############################################

def call_add_ls(message, *data):
    state.user_id = data[0]
    state.step = 0
    if settings.DEBUG:
        print(f'call_add_ls:state.user_id={state.user_id}')
    bot.send_message(message.chat.id, f'Введите номер лицевого счета (только цифры, не более 8 цифр).')


#############################################
def call_show_ls(message, *data):
    user_id = data[0]
    ls = data[1]
    kv = data[2]
    state.step = 0
    if settings.DEBUG:
        print(f'call_show_ls:user_id={user_id},kv={kv}, ls={ls}')
    bot.send_message(message.chat.id, f"Получение списка счётчиков... ожидайте.")
    try:
        user = User.objects.get(ls=ls)
        mes = (f"Лицевой счет № {ls}\n"
               f"Адрес: {user.address}\n")
        keyboard = types.InlineKeyboardMarkup()
        # цикл для счетчиков
        # dev = MeterDev.objects.filter(kv=kv)
        # print(dev)
        mes += f"Выберите прибор учета из списка"
        for pu, pu_d in MeterDev.TYPE_SELECT:
            # print(f'pu_d:{pu_d}, pu:{pu}')
            btn_meter = types.InlineKeyboardButton(f"{pu_d}",
                                                   callback_data=f'call_add_pokazaniya:{user_id}:{kv}:'
                                                                 f'{pu}:{ls}')
            keyboard.add(btn_meter)

        btn_back = types.InlineKeyboardButton("⬅️ Возврат в начало", callback_data=f'call_all_ls:{user_id}')
        btn_del = types.InlineKeyboardButton("❌ Отвязать счет", callback_data=f'call_del_ls:{user_id}:{ls}:{kv}')
        keyboard.add(btn_back, btn_del)
        sent_mess = bot.send_message(message.chat.id, mes, reply_markup=keyboard)
        state.last_message_ids.append(sent_mess.message_id)

    except User.DoesNotExist:
        bot.send_message(message.chat.id, f"Лицевой счет № {ls} не найден!")


#############################################
def call_all_ls(message, user_id):
    if settings.DEBUG:
        print(f'call_all_ls:user_id={user_id}')
    user_bot = UsersBot.objects.filter(user_id=user_id)
    # print(f'user_bot:{user_bot}')
    keyboard = types.InlineKeyboardMarkup()
    if user_bot:
        for u_b in user_bot:
            btn_show_ls = types.InlineKeyboardButton(f"🏠 {u_b.ls}-{u_b.kv}", callback_data=f'call_show_ls:{user_id}'
                                                                                           f':{u_b.ls}:'
                                                                                           f'{u_b.kv}')
            keyboard.add(btn_show_ls)
    btn_add_ls = types.InlineKeyboardButton("🔍 Добавить лицевой счет", callback_data=f'call_add_ls:{user_id}')

    keyboard.add(btn_add_ls)
    sent_mess = bot.send_message(message.chat.id, f'Выберите Лицевой счёт из списка, либо добавьте новый',
                                 reply_markup=keyboard)
    state.last_message_ids.append(sent_mess.message_id)


#############################################
def call_add_pokazaniya(message, *data):
    user_id = data[0]
    kv = data[1]
    pu_type = data[2]
    ls = data[3]
    state.kv = kv
    state.ls = ls
    state.user_id = user_id
    if settings.DEBUG:
        print(f'call_add_pokazaniya:user_id={user_id},kv={kv},pu_type={pu_type}, ls={ls}')
    if pu_type == 'hv':
        state.step = 1
    elif pu_type == 'gv':
        state.step = 2
    elif pu_type == 'e':
        state.step = 3

    p = []
    # try:
    #     num_pu = MeterDev.objects.get(kv=kv, type=pu_type)
    # except MeterDev.DoesNotExist:
    #     bot.send_message(message.chat.id, f'Прибор не найден')
    try:
        pokaz_dev = list(Pokazaniya.objects.filter(kv=kv).order_by("-date").values())
        if pokaz_dev:
            p = pokaz_dev[0]
        # print(p['date'])
    except Pokazaniya.DoesNotExist:
        bot.send_message(message.chat.id, f'Показания не найдены')
    keyboard = types.InlineKeyboardMarkup()
    date_mess = p['date'].strftime('%d.%m.%Y')
    type_display = dict(MeterDev.TYPE_SELECT).get(pu_type, 'Неизвестный тип')
    mes = (f'Прибор учета:{type_display}\n'
           f'Предыдущие:{p[pu_type]} ({date_mess})\n'
           f'Введите текущее показание ниже :')
    btn_back = types.InlineKeyboardButton("⬅️ Возврат к списку счетчиков", callback_data=f'call_show_ls:'
                                                                                         f'{user_id}:'
                                                                                         f'{ls}:{kv}')
    keyboard.add(btn_back)
    sent_mess = bot.send_message(message.chat.id, mes, reply_markup=keyboard)
    state.last_message_ids.append(sent_mess.message_id)


#############################################
def call_del_ls(message, *data):
    user_id = data[0]
    ls = data[1]
    kv = data[2]
    if settings.DEBUG:
        print(f'call_del_ls:user_id={user_id},ls={ls},kv={kv}')
    try:
        user = User.objects.get(ls=ls)
    except User.DoesNotExist:
        bot.send_message(message.chat.id, f"Лицевой счет № {ls} не найден!")

    keyboard = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("Да", callback_data=f'call_del_ls_yes:{user_id}:{ls}:{kv}')
    btn_no = types.InlineKeyboardButton("Нет", callback_data=f'call_show_ls:{user_id}:{ls}:{kv}')
    keyboard.add(btn_yes, btn_no)
    sent_mess = bot.send_message(message.chat.id, f'Вы точно хотите отвязать Лицевой счет?\n'
                                                  f'Счет № {ls}\n'
                                                  f'Адрес: {user.address}',
                                 reply_markup=keyboard)
    state.last_message_ids.append(sent_mess.message_id)


#############################################
def call_del_ls_yes(message, *data):
    user_id = data[0]
    ls = data[1]
    kv = data[2]
    if settings.DEBUG:
        print(f'call_del_ls_yes:user_id={user_id},ls={ls},kv={kv}')
    try:
        u = UsersBot.objects.get(user_id=user_id, ls=ls)
        u.delete()
        bot.send_message(message.chat.id, f'Лицевой счет №{ls} успешно отвязан!')
        if settings.DEBUG:
            print(f"del_yes:{user_id}")
        call_all_ls(message, user_id)
    except UsersBot.DoesNotExist:
        mes = f"Лицевой счет № {ls} не найден!"
        bot.send_message(message.chat.id, mes)


#############################################
def delete_messages(message):
    if state.last_message_ids:
        for lst in state.last_message_ids:
            try:
                bot.delete_message(message.chat.id, lst)
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")
        state.last_message_ids.clear()


##############################################
# обработка входящего текста
@bot.message_handler(content_types=['text'])
def func(message):
    if state.step == 0:
        if len(message.text) == 8:
            try:
                state.ls = int(message.text)
                bot.send_message(message.chat.id,
                                 text="Очень хорошо! Теперь введите номер квартиры (не более 3 символов).")
                state.step = 4
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Вы ввели некорректное значение! Введите номер лицевого счета еще раз")

        else:
            bot.send_message(message.chat.id,
                             text="Вы ввели некорректное значение! Введите номер лицевого счета еще раз")
    elif state.step == 1:
        if 1 <= len(message.text) <= 8:  # длина показаний
            try:
                val = int(message.text)
                bot.send_message(message.chat.id,
                                 text=f"Введено показание: {val}... ожидайте")
                try:
                    req = PokazaniyaUser.objects.filter(date=date.today(), kv=state.kv)
                    if req:
                        req.update(hv=val)
                    else:
                        PokazaniyaUser.objects.create(kv=state.kv, hv=val)
                except IntegrityError:
                    print("Ошибка")
                bot.send_message(message.chat.id,
                                 text=f"Показания приняты успешно!")
                data = [state.user_id, state.ls, state.kv]
                call_show_ls(message, *data)
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Введено некорректное число. Попробуйте еще раз:")
        else:
            bot.send_message(message.chat.id,
                             text="Количество символов превышает 8. Попробуйте еще раз:")
    elif state.step == 2:
        if 1 <= len(message.text) <= 8:  # длина показаний
            try:
                val = int(message.text)
                bot.send_message(message.chat.id,
                                 text=f"Введено показание: {val}... ожидайте")
                try:
                    req = PokazaniyaUser.objects.filter(date=date.today(), kv=state.kv)
                    if req:
                        req.update(gv=val)
                    else:
                        PokazaniyaUser.objects.create(kv=state.kv, gv=val)
                except IntegrityError:
                    print("Ошибка")
                bot.send_message(message.chat.id,
                                 text=f"Показания приняты успешно!")
                data = [state.user_id, state.ls, state.kv]
                call_show_ls(message, *data)
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Введено некорректное число. Попробуйте еще раз:")
        else:
            bot.send_message(message.chat.id,
                             text="Количество символов превышает 8. Попробуйте еще раз:")
    elif state.step == 3:
        if 1 <= len(message.text) <= 8:  # длина показаний
            try:
                val = int(message.text)
                bot.send_message(message.chat.id,
                                 text=f"Введено показание: {val}... ожидайте")
                try:
                    req = PokazaniyaUser.objects.filter(date=date.today(), kv=state.kv)
                    if req:
                        req.update(e=val)
                    else:
                        PokazaniyaUser.objects.create(kv=state.kv, e=val)
                except IntegrityError:
                    print("Ошибка")
                bot.send_message(message.chat.id,
                                 text=f"Показания приняты успешно!")
                data = [state.user_id, state.ls, state.kv]
                call_show_ls(message, *data)
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Введено некорректное число. Попробуйте еще раз:")
        else:
            bot.send_message(message.chat.id,
                             text="Количество символов превышает 8. Попробуйте еще раз:")
    elif state.step == 4:
        if 1 <= len(message.text) <= 3:
            try:
                state.kv = int(message.text)
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Вы ввели некорректное значение! Введите номер квартиры еще раз")

            if state.ls and state.kv:
                bot.send_message(message.chat.id, text="Подождите, идёт поиск и привязка лицевого счета..")
                u = User.objects.filter(ls=state.ls, kv=state.kv)
                if u:
                    # добавляем данные телеграм user и лицевой
                    try:
                        if UsersBot.objects.filter(ls=state.ls, user_id=message.from_user.id):
                            bot.send_message(message.chat.id,
                                             text=f"⛔ Лицевой счет уже добавлен!")
                        else:
                            if message.from_user.username:
                                UsersBot.objects.create(user_id=message.from_user.id,
                                                        username=message.from_user.username,
                                                        ls=state.ls,
                                                        kv=state.kv)
                            else:
                                UsersBot.objects.create(user_id=message.from_user.id,
                                                        ls=state.ls,
                                                        kv=state.kv)
                            bot.send_message(message.chat.id, text=f"Лицевой счет №{state.ls} успешно добавлен.")
                    except Exception as e:
                        bot.send_message(message.chat.id, text=f"Ошибка... {e}.")
                    state.step = 10
                    call_all_ls(message, message.from_user.id)
                else:
                    bot.send_message(message.chat.id,
                                     text="Не удалось найти указанный лицевой счет! Обратитесь в офис ТСН")
                    state.step = 10
                    call_all_ls(message, message.from_user.id)
        else:
            bot.send_message(message.chat.id,
                             text="Вы ввели некорректное значение! Введите номер квартиры еще раз")
    else:
        bot.send_message(message.chat.id,
                         text="Вы ввели некорректную команду!")
        delete_messages(message)
        call_all_ls(message, message.from_user.id)
