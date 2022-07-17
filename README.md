# Социальная сеть Yatube

### Как установить проект:

Клонируем репозеторий с GitHub:
```
git clone https://github.com/ggerasyanov/hw05_final.git
```
Перейти в корневую папку проекта:
```
cd .../hw05_final/
```
Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
Обновить менеджер пакетов pip:
```
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции:
```
# .../hw05_final/yatube/
python manage.py migrate
```
Проект готов к работе.

### Запустить проект:
```
python manage.py runserver
```

### Описание:
В проекте можно создать свою страничку и публиковать туда записи. Другие люди могу подписаться на автора и комментировать их посты. Есть возможность создать группы по интересам и публиковать посты и туда. Так же код проекта покрыт тестами.
