from django import forms


class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label='Сообщение')
    id_list = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        id_list = kwargs.pop('id_list', [])
        super().__init__(*args, **kwargs)
        self.fields['id_list'].initial = ','.join(id_list)  # Преобразуем список в строку

