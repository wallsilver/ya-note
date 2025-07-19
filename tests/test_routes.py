from http import HTTPStatus

from django.contrib.auth import get_user_model

from .test_base import NotesTestBase

User = get_user_model()


class TestRoutes(NotesTestBase):
    """Тестирование доступности маршрутов приложения."""

    def test_status_codes(self):
        """Проверка всех статус-кодов."""
        test_cases = [
            (None, self.home_url, 'get', HTTPStatus.OK),
            (None, self.login_url, 'get', HTTPStatus.OK),
            (None, self.logout_url, 'post', HTTPStatus.OK),
            (None, self.signup_url, 'get', HTTPStatus.OK),
            (self.reader_client, self.list_url, 'get', HTTPStatus.OK),
            (self.reader_client, self.success_url, 'get', HTTPStatus.OK),
            (self.reader_client, self.add_url, 'get', HTTPStatus.OK),
            (self.author_client, self.edit_url, 'get', HTTPStatus.OK),
            (self.author_client, self.delete_url, 'get', HTTPStatus.OK),
            (self.author_client, self.detail_url, 'get', HTTPStatus.OK),
            (self.reader_client, self.edit_url, 'get', HTTPStatus.NOT_FOUND),
            (self.reader_client, self.delete_url, 'get', HTTPStatus.NOT_FOUND),
            (self.reader_client, self.detail_url, 'get', HTTPStatus.NOT_FOUND),
        ]

        for client, url, method, expected_status in test_cases:
            with self.subTest(url=url, method=method):
                test_client = client if client else self.client
                response = getattr(test_client, method)(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректа анонимного пользователя на страницу входа."""
        test_urls = (
            self.list_url,
            self.success_url,
            self.add_url,
            self.edit_url,
            self.delete_url,
            self.detail_url,
        )
        for url in test_urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
