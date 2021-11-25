# Yatube
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
Социальная сеть блогеров (Проект Яндекс.Практикум)

# Описание
Социальная сеть для публикации личных дневников. Это сайт, на котором можно создать свою страницу. Если на нее зайти, то можно посмотреть все записи автора. Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи. Автор может выбрать имя и уникальный адрес для своей страницы. Администратор имеет возможность модерировать записи и блокировать пользователей, если начнут присылать спам. Записи можно отправить в группу и посмотреть в ней записи разных авторов.

# Системные требования

- [Python 3](https://www.python.org/)
- [Django 3.0.5](https://www.djangoproject.com/)

# установка
Склонировать проект:

      https://github.com/toshiharu13/Yatube_final.git
      
Установить зависимости:

       pip install -r requirements.txt
       
Создать и применить миграции:

      python manage.py makemigrations
      python manage.py migrate
       
Запусить Django сервер:
       
      python manage.py runserver

