from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    """Класс для удобной работы в админке. Изменяет вид отображения постов.
    Добавляет поиск и возможность сортировки для модели Post"""
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    list_editable = ('group', )
    search_fields = ('text', )
    list_filter = ('pub_date', )
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Класс для удобной работы в админке. Изменяет вид отображения групп.
    Добавляет поиск и возможность сортировки для модели Group."""
    list_display = ('title', 'slug', 'description',)
    search_fields = ('title', 'description',)
    list_filter = ('title', )
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """Класс для удобной работы в админке. Изменяет вид отображения подписок.
    Добавляет поиск и возможность сортировки для модели Follow."""
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """Класс для удобной работы в админке. Изменяет вид отображения
    комментариев. Добавляет поиск и возможность сортировки для модели Follow."""
    list_display = ('post', 'author', 'text', 'created')
    search_fields = ('text', 'author')
    list_filter = ('post', 'author', 'created')
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Comment, CommentAdmin)
