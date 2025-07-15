# news/tests/test_routes.py
from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем класс заметки.
from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):
    """Тестирование доступности маршрутов приложения."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных: пользователей и заметки."""
        # Создаём автора и читателя.
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        # Создаём заметку от имени автора.
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=cls.author,
            slug='test-note'
        )

    def test_pages_availability(self):
        """
        Проверка доступности общедоступных страниц.

        Тестируем:
        - главную страницу
        - страницу входа
        - страницу выхода (POST-запрос)
        - страницу регистрации
        """
        urls = (
            ('notes:home', None, 'get'),
            ('users:login', None, 'get'),
            ('users:logout', None, 'post'),
            ('users:signup', None, 'get'),
        )
        for name, args, method in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                if method == 'get':
                    response = self.client.get(url)
                else:
                    response = self.client.post(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_list_done_add(self):
        """
        Проверка доступности страниц для авторизованного пользователя.

        Тестируем:
        - список заметок
        - страницу успешного действия
        - страницу добавления заметки
        """
        user = self.author
        self.client.force_login(user)
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(user=user, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_detail_edit_and_delete(self):
        """
        Проверка доступности страниц редактирования,
        удаления и просмотра заметки.

        Тестируем:
        - автору доступны все страницы
        - другому пользователю возвращается 404
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Проверка редиректа анонимного пользователя на страницу входа.

        Тестируем, что при попытке доступа к защищенным страницам
        анонимный пользователь перенаправляется на страницу входа
        с параметром next, содержащим исходный URL.
        """
        login_url = reverse('users:login')
        test_cases = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:edit', self.note.slug),
            ('notes:delete', self.note.slug),
            ('notes:detail', self.note.slug),
        )

        for name, slug in test_cases:
            with self.subTest(name=name):
                url = reverse(name, args=(slug,)) if slug else reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
