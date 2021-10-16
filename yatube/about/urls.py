from django.urls import path

from .views import AboutAuthorView, AboutTechView, thank_you, wish_me

app_name = 'about'

urlpatterns = [
    path('author/', AboutAuthorView.as_view(), name='author'),
    path('tech/', AboutTechView.as_view(), name='tech'),
    path('wish_me/', wish_me, name='wish_me'),
    path('thank_you/', thank_you),
]
