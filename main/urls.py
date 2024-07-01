from django.urls import path, re_path
from django.views.generic.base import TemplateView
from .views import *

urlpatterns = [
    # path("robots.txt",TemplateView.as_view(template_name="koleso/robots.txt", content_type="text/plain"),),
    path('', index, name='home'),
    path('contact/', contact, name='contact'),
    path('info/<slug:id_slug>/', show_info, name='show_info'),
    path('docs/<slug:id_slug>/', doc_list, name='doc_list'),
    path('doc/<slug:id_slug>/', show_doc, name='show_doc'),
    path('news/<slug:id_slug>/', show_news, name='show_news'),
    path('news_list/', news_list, name='news_list'),

]