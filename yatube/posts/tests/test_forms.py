import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestFormCreateAndEditPost(TestCase):
    """Класс для проверки формы создания и редактирования постов."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=TestFormCreateAndEditPost.user,
            group=TestFormCreateAndEditPost.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = TestFormCreateAndEditPost.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверяет что пост создаётся."""
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый пост',
            'group': TestFormCreateAndEditPost.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        redirect_adress = reverse(
            'posts:profile',
            args=[TestFormCreateAndEditPost.user.username]
        )
        self.assertRedirects(
            response,
            redirect_adress,
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            'Пост не создаётся в базе данных при заполнении формы',
        )
        posts = response.context['page_obj'][0]
        test_post_field = {
            'text': posts.text,
            'group': posts.group.id,
        }
        for key_field, post_field in test_post_field.items():
            data_field = form_data[key_field]
            with self.subTest(post_field=post_field):
                self.assertEqual(
                    post_field,
                    data_field,
                    'Созданный пост не совпадает с указанным',
                )

    def test_edit_post(self):
        """Проверяет что пост изменяется."""
        new_group = Group.objects.create(
            title='Новая тестовая группа',
            slug='new_test_slug',
            description='Тестовое описание',
        )
        form_data = {
            'text': 'Новый тестовый пост',
            'group': new_group.id,
        }
        page_adress = reverse(
            'posts:post_edit',
            args=[self.post.id]
        )
        response = self.authorized_client.post(
            page_adress,
            data=form_data,
            follow=True,
        )
        redirect_adress = reverse(
            'posts:post_datail',
            args=[TestFormCreateAndEditPost.post.id]
        )
        self.assertRedirects(
            response,
            redirect_adress,
        )
        edited_post = response.context['post']
        self.post.refresh_from_db()
        self.assertEqual(
            self.post,
            edited_post,
            'Пост не был отредактирован',
        )

    def test_create_post_guest_client(self):
        """Проверяет, что неавторизованный пользователь
        не может создать пост."""
        post_count = Post.objects.count()
        response = self.guest_client.get(reverse('posts:post_create'))
        redirect_adress = (
            reverse('users:login')
            + '?next='
            + reverse('posts:post_create')
        )
        self.assertRedirects(
            response,
            redirect_adress)
        self.assertEqual(
            Post.objects.count(),
            post_count,
            'Пост был создан, хотя не должен был',
        )


class TestCommentForm(TestCase):
    """Класс для проверки формы создания комментария."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth'
        )
        cls.post = Post.objects.create(
            author=TestCommentForm.user,
            text='Тестовый текст'
        )

    def setUp(self):
        self.user = TestCommentForm.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment(self):
        """Проверяет что комментарий создаётся."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый коммент',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[TestCommentForm.post.id]),
            data=form_data,
            follow=True,
        )
        redirect_adress = reverse(
            'posts:post_datail',
            args=[TestCommentForm.post.id]
        )
        self.assertRedirects(
            response,
            redirect_adress,
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count + 1,
            'Комментарий не добавился'
        )

    def test_create_guest_user_comment(self):
        """Проверяет что гость не может создать комментарий."""
        reverse_adress = reverse(
            'posts:post_edit',
            args=[TestCommentForm.post.id],
        )
        response = self.guest_client.get(reverse_adress)
        redirect_adress = (
            reverse('users:login')
            + '?next='
            + reverse('posts:post_edit', args=[TestCommentForm.post.id])
        )
        self.assertRedirects(
            response,
            redirect_adress)
