#  https://habr.com/ru/sandbox/186542/ (Создание телеграм бота на Django + pyTelegramBotApi)
from django.shortcuts import HttpResponse, get_object_or_404
import telebot
from telebot import types  # для указание типов
from django.conf import settings
from bot.models import UsersBot, UserState
from main.models import MeterDev, Pokazaniya, PokazaniyaUser
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from datetime import date

User = get_user_model()

bot = telebot.TeleBot(settings.BOT_TOKEN)


##############################################
def get_state(user_id):
    state, created = UserState.objects.get_or_create(user_id=user_id)
    return state


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
    user_id = message.from_user.id  # присваиваем id
    state = get_state(user_id)  # получаем статус пользователя
    delete_messages(state, message)
    bot.send_message(message.chat.id, "Добро пожаловать!")
    call_all_ls(state, message)
    # step 0- ожидание лицевого
    # step 1- ожидание показания ХВС
    # step 2- ожидание показания ГВС
    # step 3- ожидание показания ЭЛ-ВО
    # step 4- ожидание квартиры


##############################################
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    state = get_state(user_id)
    action, *data = call.data.split(':')
    # Удаление предыдущих сообщений
    delete_messages(state, call.message)

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
        actions[action](state, call.message, *data)


##############################################
# FUNCTION
#############################################
def call_add_ls(state, message, *data):
    state.step = 0
    state.save()
    if settings.DEBUG:
        print(f'call_add_ls:state.user_id={state.user_id}')
    bot.send_message(message.chat.id, f'Введите номер лицевого счета (только цифры, не более 8 цифр).')


#############################################
def call_all_ls(state, message):
    if settings.DEBUG:
        print(f'call_all_ls:user_id={state.user_id}')
    user_bot = UsersBot.objects.filter(user_id=state.user_id)
    keyboard = types.InlineKeyboardMarkup()
    if user_bot:
        for u_b in user_bot:
            btn_show_ls = types.InlineKeyboardButton(f"🏠 {u_b.ls}-{u_b.kv}", callback_data=f'call_show_ls:'
                                                                                           f'{state.user_id}'
                                                                                           f':{u_b.ls}:'
                                                                                           f'{u_b.kv}')
            keyboard.add(btn_show_ls)
    btn_add_ls = types.InlineKeyboardButton("🔍 Добавить лицевой счет", callback_data=f'call_add_ls:{state.user_id}')

    keyboard.add(btn_add_ls)
    sent_mess = bot.send_message(message.chat.id, f'Выберите Лицевой счёт из списка, либо добавьте новый',
                                 reply_markup=keyboard)
    state.last_message_ids.append(sent_mess.message_id)
    state.save()


#############################################
def call_show_ls(state, message, *data):
    state.ls = data[1]
    state.kv = data[2]

    state.step = 0
    if settings.DEBUG:
        print(f'call_show_ls:user_id={state.user_id},kv={state.kv}, ls={state.ls}')
    bot.send_message(message.chat.id, f"Получение списка счётчиков... ожидайте.")
    try:
        user = User.objects.get(ls=state.ls)
        mes = (f"Лицевой счет № {state.ls}\n"
               f"Адрес: {user.address}\n")
        keyboard = types.InlineKeyboardMarkup()
        # цикл для счетчиков
        mes += f"Выберите прибор учета из списка"
        for pu, pu_d in MeterDev.TYPE_SELECT:
            btn_meter = types.InlineKeyboardButton(f"{pu_d}",
                                                   callback_data=f'call_add_pokazaniya:{pu}')
            keyboard.add(btn_meter)

        btn_back = types.InlineKeyboardButton("⬅️ Возврат в начало", callback_data=f'call_all_ls')
        btn_del = types.InlineKeyboardButton("❌ Отвязать счет", callback_data=f'call_del_ls:{state.user_id}:{state.ls}'
                                                                              f':{state.kv}')
        keyboard.add(btn_back, btn_del)
        sent_mess = bot.send_message(message.chat.id, mes, reply_markup=keyboard)
        state.last_message_ids.append(sent_mess.message_id)

    except User.DoesNotExist:
        bot.send_message(message.chat.id, f"Лицевой счет № {state.ls} не найден!")
    state.save()


#############################################
def call_add_pokazaniya(state, message, *data):
    pu_type = data[0]
    if settings.DEBUG:
        print(f'call_add_pokazaniya:user_id={state.user_id},kv={state.kv},pu_type={pu_type}, ls={state.ls}')
    if pu_type == 'hv':
        state.step = 1
    elif pu_type == 'gv':
        state.step = 2
    elif pu_type == 'e':
        state.step = 3

    p = []
    try:
        pokaz_dev = list(Pokazaniya.objects.filter(kv=state.kv).order_by("-date").values())
        if pokaz_dev:
            p = pokaz_dev[0]
    except Pokazaniya.DoesNotExist:
        bot.send_message(message.chat.id, f'Показания не найдены')
    keyboard = types.InlineKeyboardMarkup()
    date_mess = p['date'].strftime('%d.%m.%Y')
    type_display = dict(MeterDev.TYPE_SELECT).get(pu_type, 'Неизвестный тип')
    mes = (f'Прибор учета:{type_display}\n'
           f'Предыдущие:{p[pu_type]} ({date_mess})\n'
           f'Введите текущее показание ниже :')
    btn_back = types.InlineKeyboardButton("⬅️ Возврат к списку счетчиков", callback_data=f'call_show_ls:'
                                                                                         f'{state.user_id}:'
                                                                                         f'{state.ls}:{state.kv}')
    keyboard.add(btn_back)
    sent_mess = bot.send_message(message.chat.id, mes, reply_markup=keyboard)
    state.last_message_ids.append(sent_mess.message_id)
    state.save()


#############################################
def call_del_ls(state, message, *data):
    ls = data[1]
    kv = data[2]
    if settings.DEBUG:
        print(f'call_del_ls:user_id={state.user_id},ls={ls},kv={kv}')
    try:
        user = User.objects.get(ls=ls)
    except User.DoesNotExist:
        bot.send_message(message.chat.id, f"Лицевой счет № {ls} не найден!")

    keyboard = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("Да", callback_data=f'call_del_ls_yes:{state.user_id}:{ls}:{kv}')
    btn_no = types.InlineKeyboardButton("Нет", callback_data=f'call_show_ls:{state.user_id}:{ls}:{kv}')
    keyboard.add(btn_yes, btn_no)
    sent_mess = bot.send_message(message.chat.id, f'Вы точно хотите отвязать Лицевой счет?\n'
                                                  f'Счет № {ls}\n'
                                                  f'Адрес: {user.address}',
                                 reply_markup=keyboard)
    state.last_message_ids.append(sent_mess.message_id)
    state.save()


#############################################
def call_del_ls_yes(state, message, *data):
    ls = data[1]
    kv = data[2]
    if settings.DEBUG:
        print(f'call_del_ls_yes:user_id={state.user_id},ls={ls},kv={kv}')
    try:
        u = UsersBot.objects.get(user_id=state.user_id, ls=ls)
        u.delete()
        bot.send_message(message.chat.id, f'Лицевой счет №{ls} успешно отвязан!')
        if settings.DEBUG:
            print(f"del_yes:{state.user_id}")
        call_all_ls(state, message)
    except UsersBot.DoesNotExist:
        bot.send_message(message.chat.id, f"Лицевой счет № {ls} не найден!")


#############################################
def delete_messages(state, message):
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
    state = get_state(message.from_user.id)
    if state.step == 0:
        if len(message.text) == 8:
            try:
                state.ls = int(message.text)
                bot.send_message(message.chat.id,
                                 text="Очень хорошо! Теперь введите номер квартиры (не более 3 символов).")
                state.step = 4
                state.save()
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
                call_show_ls(state, message, *data)
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
                call_show_ls(state, message, *data)
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
                call_show_ls(state, message, *data)
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
                state.save()
            except ValueError:
                bot.send_message(message.chat.id,
                                 text="Вы ввели некорректное значение! Введите номер квартиры еще раз")

            if state.ls and state.kv:
                bot.send_message(message.chat.id, text="Подождите, идёт поиск и привязка лицевого счета..")
                u = User.objects.filter(ls=state.ls, kv=state.kv)
                if u:
                    # добавляем данные телеграм user и лицевой
                    try:
                        if UsersBot.objects.filter(ls=state.ls, user_id=state.user_id):
                            bot.send_message(message.chat.id,
                                             text=f"⛔ Лицевой счет уже добавлен!")
                        else:
                            if message.from_user.username:
                                UsersBot.objects.create(user_id=state.user_id,
                                                        username=message.from_user.username,
                                                        ls=state.ls,
                                                        kv=state.kv)
                            else:
                                UsersBot.objects.create(user_id=state.user_id,
                                                        ls=state.ls,
                                                        kv=state.kv)
                            bot.send_message(message.chat.id, text=f"Лицевой счет №{state.ls} успешно добавлен.")
                            state.save()
                    except Exception as e:
                        bot.send_message(message.chat.id, text=f"Ошибка... {e}.")
                    state.step = 10
                    state.save()
                    call_all_ls(state, message)
                else:
                    bot.send_message(message.chat.id,
                                     text="Не удалось найти указанный лицевой счет! Обратитесь в офис ТСН")
                    state.step = 10
                    state.save()
                    call_all_ls(state, message)
        else:
            bot.send_message(message.chat.id,
                             text="Вы ввели некорректное значение! Введите номер квартиры еще раз")
    else:
        bot.send_message(message.chat.id,
                         text="Вы ввели некорректную команду!")
        delete_messages(state, message)
        call_all_ls(state, message)
