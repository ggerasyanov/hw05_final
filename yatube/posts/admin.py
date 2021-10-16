from django.contrib import admin

from .models import Group, Post, Follow


class PostAdmin(admin.ModelAdmin):
    """Класс для удобной работы в админке. Изменяет вид отображения постов в
    админке. Добавляет поиск и возможность сортировки для модели Post"""
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    list_editable = ('group', )
    search_fields = ('text', )
    list_filter = ('pub_date', )
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Класс для удобной работы в админке. Изменяет вид отображения постов в
    админке. Добавляет поиск и возможность сортировки для модели Group."""
    list_display = ('title', 'slug', 'description',)
    search_fields = ('title', 'description',)
    list_filter = ('title', )
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """Класс для удобной работы в админке. Изменяет вид отображения постов в
    админке. Добавляет поиск и возможность сортировки для модели Follow."""
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
