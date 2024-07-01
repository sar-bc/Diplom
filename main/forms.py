from multiprocessing import AuthenticationError
from django import forms
from .models import UserMessage
from captcha.fields import CaptchaField
from django.forms import ModelForm
from main.models import PokazaniyaUser
import datetime
from django.conf import settings


class AddMessageForm(forms.ModelForm):
    # captcha = CaptchaField()
    class Meta:
        model = UserMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': 'Ваше имя', 'class': 'form-control form-value text-box single-line'}),
            'email': forms.EmailInput(
                attrs={'placeholder': 'E-mail', 'class': 'form-control form-value text-box single-line'}),
            'phone': forms.TextInput(
                attrs={'type': 'tel', 'placeholder': '+7 (999) 111 3333', 'id': 'online_phone', 'class': 'form-control',
                    'pattern': '[+]{1}7 [(]{1}[0-9]{3}[)]{1} [0-9]{3} [0-9]{4}'}),
            'message': forms.Textarea(
                attrs={'placeholder': 'Сообщение', 'class': 'form-control form-value', 'cols': 20, 'rows': 4}),
        }




# форма передачи показаний
class PokazaniyaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data', None)
        super(PokazaniyaForm, self).__init__(*args, **kwargs)
        if data:
            self.fields['kv'] = forms.IntegerField(
            widget=forms.NumberInput(attrs={'type': 'hidden', 'name': 'kv', 'value': data.kv})
        )
    cur_time = datetime.datetime.now()
    if cur_time.day in settings.DAY_PERIOD:
        hv = forms.CharField(label='Холодная вода',
                             widget=forms.NumberInput(
                                 attrs={'placeholder': 'Холодная вода', 'min': 0})
                             )
        gv = forms.CharField(label='Горячая вода',
                             widget=forms.NumberInput(
                                 attrs={'placeholder': 'Горячая вода', 'min': 0})
                             )
        e = forms.CharField(label='Электричество',
                            widget=forms.NumberInput(
                                attrs={'placeholder': 'Электричество', 'required': 'False', 'min': 0})
                            )
    else:
        kv = forms.IntegerField(
            widget=forms.NumberInput(attrs={'type': 'hidden', 'name': 'kv', 'value': 0})
        )
        hv = forms.CharField(label='Холодная вода',
                             widget=forms.NumberInput(
                                 attrs={'placeholder': 'Холодная вода', 'disabled': 'True'})
                             )
        gv = forms.CharField(label='Горячая вода',
                             widget=forms.NumberInput(
                                 attrs={'placeholder': 'Горячая вода', 'disabled': 'True'})
                             )
        e = forms.CharField(label='Электричество',
                            widget=forms.NumberInput(
                                attrs={'placeholder': 'Электричество', 'disabled': 'True'})
                            )

    class Meta:
        model = PokazaniyaUser
        fields = ['kv', 'hv', 'gv', 'e']

