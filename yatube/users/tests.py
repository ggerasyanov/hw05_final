from django.test import Client, TestCase


class StaticURLTests(TestCase):
    """Класс для проверки url-ов."""
    def setUp(self):
        self.guest_client = Client()

    def test_all_url_exists_at_desired_location(self):
        """Проверяет достпность страниц."""
        url_name = [
            '/auth/logout/',
            '/auth/signup/',
            '/auth/login/',
        ]
        for adress in url_name:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(
                    response.status_code,
                    200,
                    f'Адресс {adress} не доступен'
                )

    def test_urls_uses_correct_template_guest(self):
        """Проверяет соответсвие адресов к шаблонам."""
        templates_url_names = {
            '/auth/logout/': 'users/logged_out.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
        }
        for adress, template in templates_url_names.items():
            response = self.guest_client.get(adress)
            self.assertTemplateUsed(
                response,
                template,
                f'Адресс {adress} работает не правильно'
            )
