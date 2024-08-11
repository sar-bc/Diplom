from django.shortcuts import HttpResponse
import telebot
from telebot import types  # для указание типов
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt

bot = telebot.TeleBot(settings.BOT_TOKEN)


@csrf_exempt
def index(request):
    bot.set_webhook('https://d68a-31-29-225-89.ngrok-free.app/bot/')
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])

    return HttpResponse('<h1>Ты подключился!</h1>')


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):

    name = ''
    if message.from_user.last_name is None:
        name = f'{message.from_user.first_name}'
    else:
        name = f'{message.from_user.first_name} {message.from_user.last_name}'
    bot.send_message(message.chat.id, f'Введите номер лицевого счета (только цифры, не более 8 цифр).')
