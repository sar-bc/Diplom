from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.db import models
from django.contrib.auth.forms import PasswordChangeForm
import datetime
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

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
            if data.check_email:
                self.fields['email'] = forms.EmailField(label='E-mail', required=False, widget=forms.TextInput(
                    attrs={'class': 'form-control ', 'value': data.email, 'required':
                        'False',
                           'disabled': 'True'}))
            else:
                if data.email:
                    self.fields['email'] = forms.EmailField(label='E-mail', required=False, widget=forms.TextInput(
                        attrs={'class': 'form-control input_email_red', 'value': data.email, 'required':
                            'False',
                               'disabled': 'True'}))
                else:
                    self.fields['email'] = forms.EmailField(label='E-mail', required=False, widget=forms.TextInput(
                        attrs={'class': 'form-control', 'value': data.email, 'required':
                            'False',
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
                attrs={'class': 'form-control form-value', 'value': data.email}))
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


class UserImportForm(forms.Form):
    csv_file = forms.FileField(label="CSV Файл с лицевыми счетами")


class ReceiptsImportForm(forms.Form):
    date = forms.DateField(label="Выбирите месяц и год",
                           initial=datetime.date.today,
                           widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", 'class': 'datepicker'}),
                           input_formats=["%Y-%m-%d"])
    # year = forms.CharField(label="Год",
    #                        initial=datetime.date.year,
    #                        widget=forms.NumberInput())
    pdf_file = forms.FileField(label="PDF файл с платежками")


CHOICES_MONTH = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь"
}


class Lk_receiptForm(forms.Form):
    month = forms.DateField(
        widget=forms.Select(
            choices=CHOICES_MONTH)
    )
    year = forms.DateField(
        widget=forms.Select(
            attrs={'value': datetime.date.year},
            choices={y: y for y in range(2024, 2030)})

    )


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'kv')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
