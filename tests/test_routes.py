from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тестирование доступности маршрутов приложения."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных: пользователей и заметки."""
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=cls.author,
            slug='test-note'
        )
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.home_url = reverse('notes:home')
        cls.list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_status_codes(self):
        """Проверка всех статус-кодов в одном тесте."""
        test_cases = [
            (None, self.home_url, 'get', HTTPStatus.OK),
            (None, self.login_url, 'get', HTTPStatus.OK),
            (None, self.logout_url, 'post', HTTPStatus.OK),
            (None, self.signup_url, 'get', HTTPStatus.OK),
            (self.reader, self.list_url, 'get', HTTPStatus.OK),
            (self.reader, self.success_url, 'get', HTTPStatus.OK),
            (self.reader, self.add_url, 'get', HTTPStatus.OK),
            (self.author, self.edit_url, 'get', HTTPStatus.OK),
            (self.author, self.delete_url, 'get', HTTPStatus.OK),
            (self.author, self.detail_url, 'get', HTTPStatus.OK),
            (self.reader, self.edit_url, 'get', HTTPStatus.NOT_FOUND),
            (self.reader, self.delete_url, 'get', HTTPStatus.NOT_FOUND),
            (self.reader, self.detail_url, 'get', HTTPStatus.NOT_FOUND),
        ]

        for user, url, method, expected_status in test_cases:
            with self.subTest(url=url, user=user):
                if user:
                    self.client.force_login(user)
                response = self.client.get(
                    url) if method == 'get' else self.client.post(url)
                self.assertEqual(response.status_code, expected_status)
                if user:
                    self.client.logout()

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
