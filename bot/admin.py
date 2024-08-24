from django.contrib import admin
from .models import UsersBot
from .forms import MessageForm
from django.shortcuts import render, redirect
import requests
from django.conf import settings
from django.contrib import messages
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect




@admin.register(UsersBot)
class UsersBotAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'ls', 'kv')  # Добавьте ссылку для отправки сообщения
    actions = ['add_message']

    def add_message(self, request, queryset):
        # Создаем строку параметров из ID queryset
        ids = ','.join(str(obj.user_id) for obj in queryset)
        return HttpResponseRedirect(f"{reverse('bot:send_message')}?ids={ids}")

    add_message.short_description = 'Отправить сообщение'
