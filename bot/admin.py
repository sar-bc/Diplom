from django.contrib import admin
from .models import UsersBot


@admin.register(UsersBot)
class UsersBotAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'ls', 'kv')
