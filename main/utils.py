from main.models import Info, KatDoc, Card
import datetime

infos = Info.objects.all().order_by('id')
kat_doc = KatDoc.objects.all().order_by('id')
cards = Card.objects.all().order_by('id')[:3]
year = datetime.date.today().year
