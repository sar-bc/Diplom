from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from .forms import *
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from .utils import paginate

# return HttpResponse(f"Отображение статьи с id = {post_id}")
col = 6  # для пагинации


#########################################################################################
def index(request):
    news = News.objects.all().order_by('-id')[:3]
    context = {
        'title': 'Главная',
        'news': news,
    }
    return render(request, 'main/index.html', context)


#########################################################################################
def contact(request):
    if request.method == 'POST':
        form = AddMessageForm(request.POST)
        if form.is_valid():
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
        'form': form,
    }
    return render(request, 'main/contact.html', context)


#########################################################################################
def show_info(request, id_slug):
    info = get_object_or_404(Info, slug=id_slug)
    context = {
        'info': info,
    }
    return render(request, 'main/info.html', context)


#########################################################################################
def doc_list(request, id_slug):
    title = KatDoc.objects.get(slug=id_slug)
    docs_list = Doc.objects.all().filter(kat_id__slug=id_slug)
    # Постраничная разбивка с col постами на страницу
    custom_range, docs = paginate(request, docs_list, 6)

    context = {
        'title': title.name,
        'custom_range': custom_range,
        'docs': docs,
    }
    return render(request, 'main/doc_list.html', context)


#########################################################################################
def show_doc(request, id_slug):
    document = get_object_or_404(Doc, slug=id_slug)
    count = document.views + 1
    document.views = count
    document.save(update_fields=['views'])
    context = {
        'document': document,
        'count': count
    }
    return render(request, 'main/show_doc.html', context)


#########################################################################################
def show_news(request, id_slug):
    document = get_object_or_404(News, slug=id_slug)
    count = document.views + 1
    document.views = count
    document.save(update_fields=['views'])
    context = {
        'document': document,
        'count': count
    }
    return render(request, 'main/show_news.html', context)


#########################################################################################
def news_list(request):
    news_list = News.objects.all().order_by('-id')
    # Постраничная разбивка с col постами на страницу
    custom_range, nws = paginate(request, news_list, 6)

    context = {
        'news_list': nws,
        'custom_range': custom_range,
    }
    return render(request, 'main/news_list.html', context)


#########################################################################################
def pageNotFound(request, exception):
    context = {
        'title': 'Страница не найдена',
    }
    return render(request, 'main/page_not_found.html', context)
#########################################################################################
