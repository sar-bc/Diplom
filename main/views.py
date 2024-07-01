from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from datetime import date
import datetime
from .models import *
from .forms import *
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from main.utils import infos, kat_doc, year, cards

# return HttpResponse(f"Отображение статьи с id = {post_id}")
col = 6  # для пагинации


#########################################################################################
def index(request):
    news = News.objects.all().order_by('-id')[:3]
    context = {
        'title': 'Главная',
        'year': year,
        'cards': cards,
        'news': news,
        'infos': infos,
        'kat_doc': kat_doc,
    }
    return render(request, 'main/index.html', context=context)


#########################################################################################
def contact(request):
    news = News.objects.all().order_by('-id')[:3]
    if request.method == 'POST':
        form = AddMessageForm(request.POST)
        if form.is_valid():
            # print(form.cleaned_data)
            x = request.POST.dict()
            mess = "Новое сообщение от " + x.get('name') + "; e-mail: " + x.get('email') + "; Тел: " + x.get(
                'phone') + "; Сообщение: " + x.get('message')
            form.save()
            send_mail('Уведомление с сайта ТСН', mess, settings.EMAIL_HOST_USER,
                      [settings.EMAIL_FROM_ADMIN, settings.EMAIL_FROM_CLIENT], fail_silently=False, )
            return redirect('home')
    else:
        form = AddMessageForm()
    context = {
        'title': 'Контакты',
        'year': year,
        'cards': cards,
        'news': news,
        'infos': infos,
        'kat_doc': kat_doc,
        'form': form,

    }
    return render(request, 'main/contact.html', context=context)


#########################################################################################
def show_info(request, id_slug):
    info = get_object_or_404(Info, slug=id_slug)
    context = {
        'info': info,
        'year': year,
        'cards': cards,
        'infos': infos,
        'kat_doc': kat_doc,
    }
    return render(request, 'main/info.html', context=context)


#########################################################################################
def doc_list(request, id_slug):
    title = KatDoc.objects.get(slug=id_slug)
    docs = Doc.objects.all().filter(kat_id__slug=id_slug)
    ######################
    # Постраничная разбивка с col постами на страницу
    paginator = Paginator(docs, col)
    page_number = request.GET.get('page', 1)
    doc = paginator.page(page_number)
    page_all = paginator.page_range  # передаем количество страниц для цикла в шаблоне
    ######################
    context = {
        'title': title.name,
        'page_all': page_all,
        'docs': doc,
        'year': year,
        'cards': cards,
        'infos': infos,
        'kat_doc': kat_doc,
    }
    return render(request, 'main/doc_list.html', context=context)


#########################################################################################
def show_doc(request, id_slug):
    document = get_object_or_404(Doc, slug=id_slug)
    count = document.views + 1
    document.views = count
    document.save(update_fields=['views'])
    context = {
        'document': document,
        'year': year,
        'cards': cards,
        'infos': infos,
        'kat_doc': kat_doc,
        'count': count
    }
    return render(request, 'main/show_doc.html', context=context)


#########################################################################################
def show_news(request, id_slug):
    document = get_object_or_404(News, slug=id_slug)
    count = document.views + 1
    document.views = count
    document.save(update_fields=['views'])
    context = {
        'document': document,
        'year': year,
        'cards': cards,
        'infos': infos,
        'kat_doc': kat_doc,
        'count': count
    }
    return render(request, 'main/show_news.html', context=context)


#########################################################################################
def news_list(request):
    news_l = News.objects.all().order_by('-id')
    ######################
    # Постраничная разбивка с col постами на страницу
    paginator = Paginator(news_l, col)
    page_number = request.GET.get('page', 1)
    news = paginator.page(page_number)
    page_all = paginator.page_range  # передаем количество страниц для цикла в шаблоне
    ######################
    context = {
        'news_list': news,
        'page_all': page_all,
        'year': year,
        'cards': cards,
        'infos': infos,
        'kat_doc': kat_doc,
    }
    return render(request, 'main/news_list.html', context=context)


#########################################################################################
def pageNotFound(request, exception):
    # year = datetime.date.today().year
    # cards = Card.objects.all().order_by('id')[:3]
    context = {
        'title': 'Страница не найдена',
        'year': year,
        'cards': cards,
    }
    return render(request, 'main/page_not_found.html', context=context)
#########################################################################################
