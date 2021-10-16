from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

from .forms import WishMeForm


# Create your views here.
class AboutAuthorView(TemplateView):
    """Класс статичной страницы с наполнение 'Об авторе'."""
    template_name = "about/author.html"


class AboutTechView(TemplateView):
    """Класс статичной страницы с наполнение 'Технологии'."""
    template_name = "about/tech.html"


def send_msg(name, email, comment):
    """Функция отправки сообщения."""
    subject = f"Тебе пришло пожелание от {name}"
    body = f"""
    Вот что он тебе пожелал: {comment}
    """
    send_mail(
        subject, body, email, ["QieDie@yandex.ru", ],
    )


def thank_you(request):
    """Функция рендеринга странички благодарности."""
    return render(request, 'about/thankyou.html')


def wish_me(request):
    """Функция формы на странице отправки пожелания."""
    if request.method == 'POST':
        form = WishMeForm(request.POST)
        if form.is_valid():
            send_msg(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['comment'],
                comment=form.cleaned_data['comment'],
            )
            return redirect('/about/thank_you/')
        return render(request, 'about/wish_me.html', {'form': form})
    form = WishMeForm()
    return render(request, 'about/wish_me.html', {'form': form})
