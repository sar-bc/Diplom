from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.db import models
from django.contrib.auth.forms import PasswordChangeForm

from django.forms import ModelForm


User = get_user_model()


class LoginUserForm(AuthenticationForm):  # forms.Form
    username = forms.CharField(label='Лицевой счет*',
                               widget=forms.TextInput(attrs={'class': 'form-control login_input'}))
    password = forms.CharField(label='Пароль*', widget=forms.PasswordInput(attrs={'class': 'form-control login_input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class EditProfile(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data', None)
        super(EditProfile, self).__init__(*args, **kwargs)
        if data:
            self.fields['fio'] = forms.CharField(label='ФИО', widget=forms.TextInput(
                attrs={'class': 'form-control form-value ', 'value': data.fio, 'disabled': 'True'}))
            self.fields['phone'] = forms.Field(label='Телефон', widget=forms.TextInput(
                attrs={'type': 'tel', 'id': 'online_phone', 'class': 'form-control',
                       'pattern': '[+]{1}7 [(]{1}[0-9]{3}[)]{1} [0-9]{3} [0-9]{4}', 'value': data.phone,
                       'disabled': 'True'}))
            self.fields['email'] = forms.EmailField(label='E-mail', required=False, widget=forms.TextInput(
                attrs={'class': 'form-control form-value ', 'value': data.email, 'required': 'False',
                       'disabled': 'True'}))
            self.fields['password'] = forms.CharField(label='Пароь', required=False, widget=forms.PasswordInput(
                attrs={'class': 'form-control form-value ', 'value': '0000000000000', 'required': 'False',
                       'disabled': 'True'}))


    class Meta:
        model = User
        fields = ['fio', 'phone', 'email', 'rec_doc']


class EditPhone(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data', None)
        super(EditPhone, self).__init__(*args, **kwargs)
        if data:
            self.fields['phone'] = forms.Field(label='Телефон', widget=forms.TextInput(
                attrs={'type': 'tel', 'id': 'online_phone', 'class': 'form-control',
                       'pattern': '[+]{1}7 [(]{1}[0-9]{3}[)]{1} [0-9]{3} [0-9]{4}', 'value': data.phone,
                       'placeholder': '+7 (999) 123 4455'}))

        else:
            self.fields['phone'] = forms.CharField(label='Телефон', widget=forms.TextInput(
                attrs={'type': 'tel', 'id': 'online_phone', 'class': 'form-control',
                       'pattern': '[+]{1}7 [(]{1}[0-9]{3}[)]{1} [0-9]{3} [0-9]{4}', 'placeholder': '+7 (999) 123 4455',
                       'value': ''}))

    class Meta:
        model = get_user_model()
        fields = ['phone']


class EditEmail(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data', None)
        super(EditEmail, self).__init__(*args, **kwargs)
        if data:
            self.fields['email'] = forms.EmailField(label='E-mail', required=False, widget=forms.TextInput(
                attrs={'class': 'form-control form-value ', 'value': data.email}))
        else:
            self.fields['email'] = forms.EmailField(label='E-mail', required=False, widget=forms.TextInput(
                attrs={'class': 'form-control form-value ', 'value': ''}))

    class Meta:
        model = get_user_model()
        fields = ['email']


class ChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-value ', 'autocomplete': 'current-password', 'autofocus': True}),
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-value ', 'autocomplete': 'new-password', 'autofocus': True})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-value ', 'autocomplete': 'new-password', 'autofocus': True})
    )

