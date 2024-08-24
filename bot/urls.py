from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = "bot"

urlpatterns = [
    path('', csrf_exempt(views.index), name='index'),
    path('send_message', views.send_message, name='send_message'),

]
