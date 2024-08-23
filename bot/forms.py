from django import forms


class MessageBotForm(forms.Form):
    body = forms.Textarea()
