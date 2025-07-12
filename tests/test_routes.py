# news/tests/test_routes.py
from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем класс комментария.
from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=cls.author,
            slug='test-note'
        )

    # От имени одного пользователя создаём комментарий к новости:
    # cls.note = Note.objects.create(
    #     note=cls.note,
    #     author=cls.author,
    #     text='Текст комментария'
    # )

    def test_pages_availability(self):
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

    def test_availability_detail_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Производим вход пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:edit', 'notes:delete', 'notes:detail',):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы входа:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем пересылку:
        for name, slug in (
                ('notes:list', None),
                ('notes:success', None),
                ('notes:add', None),
                ('notes:edit', 'note'),
                ('notes:delete', 'note'),
                ('notes:detail', 'note'),
        ):
            with self.subTest(name=name):
                # Получаем адрес страницы работы с заметкой или,
                # если её имя не указано, общие страницы:
                if slug:
                    url = reverse(name, args=(self.note.slug,))
                else:
                    url = reverse(name)
                # Получаем ожидаемый адрес страницы логина, на который будет
                # перенаправлен пользователь. Учитываем, что в адресе будет
                # параметр next, в котором передаётся адрес страницы,
                # с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)
