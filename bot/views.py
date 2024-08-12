from django.shortcuts import HttpResponse
import telebot
from telebot import types  # для указание типов
from django.conf import settings
from .models import UsersBot
from main.models import MeterDev, Pokazaniya, PokazaniyaUser
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

bot = telebot.TeleBot(settings.BOT_TOKEN)

last_message_id = None
last_message_id_lst = []
##############################################
res_ls = int()
res_kv = int()


##############################################


@csrf_exempt
def index(request):
    bot.set_webhook('https://847a-31-29-225-89.ngrok-free.app/bot/')
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])

    return HttpResponse('<h1>Ты подключился!</h1>')


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    global last_message_id
    global last_message_id_lst
    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id_lst:
        for lst in last_message_id_lst:
            try:
                bot.delete_message(call.message.chat.id, lst)
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")
        last_message_id_lst.clear()

    # print(message.from_user)
    # проверяем есть ли такой user и лицевой
    user_bot = UsersBot.objects.filter(user_id=message.from_user.id)
    if user_bot:
        # id есть в базе
        keyboard = types.InlineKeyboardMarkup()
        for u_b in user_bot:
            # print(f'u_b:{u_b.ls}')
            btn_show_ls = types.InlineKeyboardButton(f"🏠 {u_b.ls}-{u_b.kv}", callback_data=f'cal_show_ls'
                                                                                           f':{u_b.ls}')
            keyboard.add(btn_show_ls)

        btn_add_ls = types.InlineKeyboardButton("🔍 Добавить лицевой счет", callback_data='call_add_ls')

        keyboard.add(btn_add_ls)
        sent_mess = bot.send_message(message.chat.id, f'Выберите Лицевой счёт из списка, либо добавьте новый',
                                     reply_markup=keyboard)
        last_message_id_lst.append(sent_mess.message_id)
    else:
        # id НЕТ в базе
        keyboard = types.InlineKeyboardMarkup()
        btn_add_ls = types.InlineKeyboardButton("🔍 Добавить лицевой счет", callback_data='call_add_ls')
        keyboard.add(btn_add_ls)
        sent_mess = bot.send_message(message.chat.id, f'У вас нет добавленных лицевых счетов', reply_markup=keyboard)
        last_message_id_lst.append(sent_mess.message_id)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # Извлекаем данные из callback_data
    data = call.data.split(':')
    action = data[0]
    global last_message_id
    global last_message_id_lst

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id_lst:
        for lst in last_message_id_lst:
            try:
                bot.delete_message(call.message.chat.id, lst)
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")
        last_message_id_lst.clear()

    if action == 'call_add_ls':
        bot.send_message(call.message.chat.id, f'Введите номер лицевого счета (только цифры, не более 8 цифр).')
    elif action == 'cal_show_ls':
        ls = data[1]
        bot.send_message(call.message.chat.id, f"Получение списка счётчиков... ожидайте.")
        try:
            user = User.objects.get(ls=ls)
            mes = (f"Лицевой счет № {ls}\n"
                   f"Адрес: {user.address}\n")

            keyboard = types.InlineKeyboardMarkup()
            # цикл для счетчиков
            # mes +=f"Выберите прибор учета из списка"
            mes += f"Приборы учета не добавлены, обратитесь в офис ТСН"

            # bot.send_message(call.message.chat.id, "⛔ Не найдено счетчиков, обратитесь в офис ТСН")
            # btn_meter = types.InlineKeyboardButton("⛔ Не найдено счетчиков, обратитесь в офис ТСН", callback_data='r')
            # keyboard.add(btn_meter)
            btn_back = types.InlineKeyboardButton("⬅️ Возврат в начало", callback_data=f'call_all_ls:{ls}')
            btn_del = types.InlineKeyboardButton("❌ Отвязать счет", callback_data=f'call_del_ls:{ls}')
            keyboard.add(btn_back, btn_del)
            sent_mess = bot.send_message(call.message.chat.id, mes, reply_markup=keyboard)
            last_message_id_lst.append(sent_mess.message_id)

        except User.DoesNotExist:
            mes = f"Лицевой счет № {ls} не найден!"
            bot.send_message(call.message.chat.id, mes)
    elif action == 'call_all_ls':
        ls = data[1]
        # print(f'ls:{ls}')
        user_bot = UsersBot.objects.filter(ls=ls)
        if user_bot:
            # id есть в базе
            keyboard = types.InlineKeyboardMarkup()
            for u_b in user_bot:
                # print(f'u_b:{u_b.ls}')
                btn_show_ls = types.InlineKeyboardButton(f"🏠 {u_b.ls}-{u_b.kv}", callback_data=f'cal_show_ls:{u_b.ls}')
                keyboard.add(btn_show_ls)

            btn_add_ls = types.InlineKeyboardButton("🔍 Добавить лицевой счет", callback_data='call_add_ls')

            keyboard.add(btn_add_ls)
            sent_mess = bot.send_message(call.message.chat.id, f'Выберите Лицевой счёт из списка, либо добавьте новый',
                                         reply_markup=keyboard)
            last_message_id_lst.append(sent_mess.message_id)
    elif action == 'call_del_ls':
        ls = data[1]
        try:
            user = User.objects.get(ls=ls)
        except User.DoesNotExist:
            mes = f"Лицевой счет № {ls} не найден!"
            bot.send_message(call.message.chat.id, mes)

        keyboard = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("Да", callback_data=f'call_del_ls_yes:{ls}')
        btn_no = types.InlineKeyboardButton("Нет", callback_data=f'cal_show_ls:{ls}')
        keyboard.add(btn_yes, btn_no)
        sent_mess = bot.send_message(call.message.chat.id, f'Вы точно хотите отвязать Лицевой счет?\n'
                                                           f'Счет № {ls}\n'
                                                           f'Адрес: {user.address}',
                                     reply_markup=keyboard)
        last_message_id_lst.append(sent_mess.message_id)
    elif action == 'call_del_ls_yes':
        ls = data[1]
        try:
            u = UsersBot.objects.get(ls=ls)
            u.delete()
            bot.send_message(call.message.chat.id, f'Лицевой счет №{ls} успешно отвязан!')
            keyboard = types.InlineKeyboardMarkup()
            btn_add_ls = types.InlineKeyboardButton("🔍 Добавить лицевой счет", callback_data='call_add_ls')
            keyboard.add(btn_add_ls)
            sent_mess = bot.send_message(message.chat.id, f'У вас нет добавленных лицевых счетов',
                                         reply_markup=keyboard)
            last_message_id_lst.append(sent_mess.message_id)
        except UsersBot.DoesNotExist:
            mes = f"Лицевой счет № {ls} не найден!"
            bot.send_message(call.message.chat.id, mes)


@bot.message_handler(content_types=['text'])
def func(message):
    global res_ls
    global res_kv
    if len(message.text) == 8:
        try:
            res_ls = int(message.text)
            bot.send_message(message.chat.id,
                             text="Очень хорошо! Теперь введите номер квартиры (не более 3 символов).")
        except ValueError:
            bot.send_message(message.chat.id,
                             text="Вы ввели некорректное значение! Введите номер лицевого счета еще раз")
        # print(f'Передан лицевой:{res_ls}')

    elif 1 <= len(message.text) <= 3:
        try:
            res_kv = int(message.text)
            # print(f'Передана квартира:{res_kv}')

        except ValueError:
            bot.send_message(message.chat.id,
                             text="Вы ввели некорректное значение! Введите номер квартиры еще раз")

        if res_ls and res_kv:
            bot.send_message(message.chat.id, text="Подождите, идёт поиск и привязка лицевого счета..")
            # print(f'LS:{res_ls}; KV:{res_kv};')
            u = User.objects.filter(ls=res_ls, kv=res_kv)

            if u:
                # добавляем данные телеграм user и лицевой
                UsersBot.objects.create(user_id=message.from_user.id, username=message.from_user.username, ls=res_ls,
                                        kv=res_kv)
                bot.send_message(message.chat.id, text=f"Лицевой счет №{res_ls} успешно добавлен.")
                keyboard = types.InlineKeyboardMarkup()
                user_bot = UsersBot.objects.filter(user_id=message.from_user.id)
                for u_b in user_bot:
                    # print(f'u_b:{u_b.ls}')
                    btn_show_ls = types.InlineKeyboardButton(f"🏠 {u_b.ls}-{u_b.kv}",
                                                             callback_data=f'cal_show_ls:{u_b.ls}')
                    keyboard.add(btn_show_ls)

                btn_add_ls = types.InlineKeyboardButton("🔍 Добавить лицевой счет", callback_data='call_add_ls')
                keyboard.add(btn_add_ls)
                sent_mess = bot.send_message(message.chat.id, f'Выберите Лицевой счёт из списка, либо добавьте новый',
                                             reply_markup=keyboard)
                last_message_id_lst.append(sent_mess.message_id)

            else:
                bot.send_message(message.chat.id, text="Не удалось найти указанный лицевой счет! Обратитесь в офис ТСН")

    else:
        bot.send_message(message.chat.id, text="Вы ввели некорректное значение! Введите номер лицевого счета еще раз")
