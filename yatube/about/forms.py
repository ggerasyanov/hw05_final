from django import forms


class WishMeForm(forms.Form):
    """Класс формы для отправки сообщения на почту."""
    name = forms.CharField(label='Ваше имя', max_length=100)
    email = forms.EmailField(label='Ваша почта')
    comment = forms.CharField(label='Пожелание', widget=forms.Textarea)


def clean_name(self):
    """Валидация поля name."""
    data = self.cleaned_data["name"]
    if data is None:
        raise forms.ValidationError('Напишите своё имя, пожалуйста')
    return data


def clean_comment(self):
    """Валидация поля comment."""
    data = self.cleaned_data["comment"]
    if data is None:
        raise forms.ValidationError('Напишите свое пожелание тут')
    return data
