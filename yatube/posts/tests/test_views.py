import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()
small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
uploaded = SimpleUploadedFile(
    name='small.gif',
    content=small_gif,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestViewsFunc(TestCase):
    """Класс для проверки правильной работы views функций."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=TestViewsFunc.user,
            group=TestViewsFunc.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user = TestViewsFunc.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Проверяет корректную работу namespase:name в приложении."""
        templates_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=[TestViewsFunc.group.slug]
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    args=[TestViewsFunc.user.username]
                    ): 'posts/profile.html',
            reverse('posts:post_datail',
                    args=[TestViewsFunc.post.id]
                    ): 'posts/post_datail.html',
            reverse('posts:post_edit',
                    args=[TestViewsFunc.post.id]
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Шаблон {template} не соответвует адресу {reverse_name}'
                )

    def test_all_page_show_correct_context(self):
        """Проверяет корректность передаваемого в views функциях
        словаря context."""
        response_views = {
            'index':
            self.authorized_client.get(reverse('posts:index')),
            'group_list':
            self.authorized_client.get(reverse(
                'posts:group_list', args=[TestViewsFunc.group.slug])),
            'profile':
            self.authorized_client.get(reverse(
                'posts:profile', args=[TestViewsFunc.user.username])),
            'post_datail':
            self.authorized_client.get(reverse(
                'posts:post_datail', args=[TestViewsFunc.post.id])),
        }

        for name_view, response in response_views.items():
            if name_view == 'index':
                page_obj = response.context['page_obj'][0]
                dict_check = {
                    'Тестовый пост': page_obj.text,
                    TestViewsFunc.user.username: page_obj.author.username,
                    TestViewsFunc.post.image: page_obj.image,
                }
            elif name_view == 'group_list':
                page_obj = response.context['page_obj'][0]
                group = response.context['group']
                dict_check = {
                    'Тестовый пост': page_obj.text,
                    TestViewsFunc.user.username: page_obj.author.username,
                    'Тестовая группа': group.title,
                    TestViewsFunc.post.image: page_obj.image,
                }
            elif name_view == 'profile':
                page_obj = response.context['page_obj'][0]
                author = response.context['author']
                dict_check = {
                    'Тестовый пост': page_obj.text,
                    TestViewsFunc.user.username: page_obj.author.username,
                    TestViewsFunc.user.username: author.username,
                    TestViewsFunc.post.image: page_obj.image,
                }
            elif name_view == 'post_datail':
                post = response.context['post']
                dict_check = {
                    'Тестовый пост': post.text,
                    TestViewsFunc.user.username: post.author.username,
                    TestViewsFunc.post.image: post.image,
                }
            for key, values in dict_check.items():
                with self.subTest(key=key):
                    self.assertEqual(
                        key,
                        values,
                        (f'Словарь context на странице {name_view} '
                         'работает не правильно'),
                    )

    def test_cache_index(self):
        """Проверяет правильную работу кэша."""
        count_posts = Post.objects.count()
        Post.objects.create(
            text='Тестовый пост 2',
            author=TestViewsFunc.user,
            group=TestViewsFunc.group,
        )
        reverse_name = reverse('posts:index')
        response = self.authorized_client.get(reverse_name)
        count_response_posts = len(response.context['page_obj'])
        self.assertEqual(count_response_posts, count_posts + 1)
        content_page = response.content
        Post.objects.get(text='Тестовый пост 2').delete()
        response = self.authorized_client.get(reverse_name)
        self.assertEqual(response.content, content_page)
        cache.clear()
        response = self.authorized_client.get(reverse_name)
        self.assertNotEqual(response.content, content_page)


class TestPaginatorView(TestCase):
    """Класс для проверки работы paginator."""
    PAGE_SIZE = 10
    POST_COUNT = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.user = User.objects.create(
            username='auth',
        )
        Post.objects.bulk_create(
            [Post(text=f'Тестовый пост {i}', author=cls.user, group=cls.group)
             for i in range(cls.POST_COUNT)]
        )

    def setUp(self):
        cache.clear()
        self.user = TestPaginatorView.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_paginator(self):
        """Проверяет корректность работы paginator на первой странице."""
        templates_pages_name = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    args=[TestPaginatorView.group.slug]),
            reverse('posts:profile',
                    args=[TestPaginatorView.user.username]),
        ]
        for reverse_name in templates_pages_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                len_paginator = len(response.context['page_obj'])
                self.assertEqual(
                    len_paginator,
                    self.PAGE_SIZE,
                    f'Паджинатор на {reverse_name} работает не правильно',
                )

    def test_second_page_paginator(self):
        """Проверяет корректность работы paginator на второй странице."""
        templates_pages_name = [
            reverse('posts:index') + '?page=2',
            reverse('posts:group_list',
                    args=[TestPaginatorView.group.slug]) + '?page=2',
            reverse('posts:profile',
                    args=[TestPaginatorView.user.username]) + '?page=2',
        ]
        for reverse_name in templates_pages_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                len_paginator = len(response.context['page_obj'])
                self.assertEqual(
                    len_paginator,
                    (self.POST_COUNT - self.PAGE_SIZE),
                    f'Паджинатор {reverse_name} работает не правильно'
                )


class TestCreatePost(TestCase):
    """Класс для проверки функция создания постов."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth',
        )
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug_1',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание',
        )
        cls.post_1 = Post.objects.create(
            text='Тестовый пост 1',
            author=TestCreatePost.user,
            group=TestCreatePost.group_1,
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый пост 2',
            author=TestCreatePost.user,
            group=TestCreatePost.group_2,
        )

    def setUp(self):
        cache.clear()
        self.user = TestCreatePost.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверяет попадает ли пост на нужные страницы
        при указании группы."""
        templates_pages_name = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    args=[TestCreatePost.group_1.slug]),
            reverse('posts:group_list',
                    args=[TestCreatePost.group_2.slug]),
            reverse('posts:profile',
                    args=[TestCreatePost.user.username]),
        ]
        for reverse_name in templates_pages_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                new_post = response.context['page_obj'][0]
                if new_post.group != TestCreatePost.group_1:
                    self.assertNotEqual(
                        new_post,
                        TestCreatePost.post_1,
                        'Пост попадает не в ту группу',
                    )
                else:
                    self.assertEqual(
                        new_post,
                        TestCreatePost.post_1,
                        ('Новый пост не соответсует '
                         f'ожиданиям на {reverse_name}')
                    )


class TestFollowViews(TestCase):
    """Класс для проверки функций подписок."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='user'
        )
        cls.author = User.objects.create(
            username='auth'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=TestFollowViews.author
        )

    def setUp(self):
        cache.clear()
        self.user = TestFollowViews.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow_authorized_client(self):
        """Проверяет возможность подсписки на автора."""
        reverse_name = reverse(
            'posts:profile_follow',
            args=[TestFollowViews.author],
        )
        self.authorized_client.get(reverse_name)
        create_object = Follow.objects.values_list('user', flat=True)
        self.assertIn(TestFollowViews.user.id, create_object)

    def test_unfollow_authoriced_client(self):
        """Проверяет возможность отписки от автора."""
        reverse_name = reverse(
            'posts:profile_unfollow',
            args=[TestFollowViews.author]
        )
        self.authorized_client.get(reverse_name)
        create_object = Follow.objects.values_list('user', flat=True)
        self.assertNotIn(TestFollowViews.user.id, create_object)

    def test_follow_index_post_follow_user(self):
        """Проверяет отображение постов авторов на которых есть подписка."""
        post_count = Post.objects.count()
        Follow.objects.create(
            user=TestFollowViews.user,
            author=TestFollowViews.author,
        )
        reverse_name_index = reverse(
            'posts:follow_index'
        )
        response = self.authorized_client.get(reverse_name_index)
        response_posts_count = len(response.context['page_obj'])
        self.assertEqual(
            post_count,
            response_posts_count
        )

    def test_follow_index_post_unfollow_user(self):
        """Проверяет что не нужные посты не появляются в подписках."""
        post_count = Post.objects.count()
        reverse_name_index = reverse(
            'posts:follow_index'
        )
        response = self.authorized_client.get(reverse_name_index)
        response_posts_count = len(response.context['page_obj'])
        self.assertEqual(
            post_count - 1,
            response_posts_count
        )
