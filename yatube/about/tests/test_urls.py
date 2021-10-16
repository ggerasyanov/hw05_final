from django.test import Client, TestCase


class StaticURLTests(TestCase):
    """Класс для проверки статичиских страниц"""
    def setUp(self):
        self.guest_client = Client()

    def test_all_url_exists_at_desired_location(self):
        """Проверяет доступность страниц."""
        url_name = [
            '/about/author/',
            '/about/tech/',
            '/about/wish_me/',
            '/about/thank_you/',
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
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
            '/about/wish_me/': 'about/wish_me.html',
            '/about/thank_you/': 'about/thankyou.html'
        }
        for adress, template in templates_url_names.items():
            response = self.guest_client.get(adress)
            self.assertTemplateUsed(
                response,
                template,
                f'Адресс {adress} работает не правильно'
            )
