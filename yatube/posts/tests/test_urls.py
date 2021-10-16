from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    """Класс для проверки правильной работы url-ов"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=StaticURLTests.group
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = StaticURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template_guest(self):
        """Проверяет соответвие адресов к шаблонам."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_datail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            authorized_templates = ['/create/', '/posts/1/edit/']
            with self.subTest(adress=adress):
                if adress in authorized_templates:
                    response = self.authorized_client.get(adress)
                    self.assertTemplateUsed(
                        response,
                        template,
                        f'Адресс {adress} использует не правильный шаблон'
                    )
                else:
                    response = self.guest_client.get(adress)
                    self.assertTemplateUsed(
                        response,
                        template,
                        f'Адресс {adress} использует не правильный шаблон'
                    )

    def test_all_url_exists_at_desired_location(self):
        """Проверяет доступность страниц для авторизованного
        и не авторизованного пользователя."""
        url_name = [
            '/',
            '/group/test_slug/',
            '/profile/auth/',
            '/posts/1/',
            '/create/',
            '/posts/1/edit/',
        ]
        for adress in url_name:
            authorized_adress = ['/create/', '/posts/1/edit/']
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                if adress in authorized_adress:
                    self.assertEqual(
                        response.status_code,
                        302,
                        f'Адресс {adress} не доступен.'
                    )
                else:
                    self.assertEqual(
                        response.status_code,
                        200,
                        f'Адресс {adress} не доступен'
                    )

    def test_access_edit_author_post(self):
        """Проверяет перенаправление на post_datail если
        пользователь не является автором."""
        if StaticURLTests.post.author != self.user:
            response = self.authorized_client.get('/posts/1/edit/',
                                                  follow=True)
            self.assertRedirects(
                response,
                '/posts/1/',
                ('Пользователя не перенаправляет на post_datail '
                 'если он не автор'),
            )
        pass
