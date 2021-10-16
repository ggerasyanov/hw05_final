from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Класс для проверки моделей."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def test_object_name_post(self):
        """Проверяет первые 15 символов поста. Тестируется метод __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(
            expected_object_name,
            str(post),
            'Метод __str__ в модели Post работает не правильно',
        )

    def test_object_name_group(self):
        """Проверяет название группы. Тестируется метод __str__"""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(
            expected_object_name,
            str(group),
            'Метод __str__ в модели Group работает не правильно',
        )
