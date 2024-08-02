from main.models import Info, KatDoc, Card
import datetime


def get_context_menu(request):
    context = {
        'year': datetime.date.today().year,
        'cards': Card.objects.all().order_by('id')[:3],
        'infos': Info.objects.all().order_by('id'),
        'kat_doc': KatDoc.objects.all().order_by('id')
    }
    return context
