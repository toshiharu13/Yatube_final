from django.urls import path

from . import views

urlpatterns = [
    path('500/', views.server_error, name='500'),
    path('404/', views.page_not_found, name='404'),
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
    path('new/', views.new_post, name='new_post'),
    # Профайл пользователя, добавил Р в путь иначе в админку не войти
    path('<str:username>/', views.profile, name='profile'),
    # Просмотр записи
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/',
            views.post_edit,
            name='post_edit'
    ),
    path("<username>/<int:post_id>/comment",
         views.add_comment, name="add_comment"
         ),
]
