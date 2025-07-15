"""Тесты для проверки логики работы с заметками."""
from http import HTTPStatus

from django.test import Client, TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import NoteForm, WARNING

User = get_user_model()


class NoteFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных: пользователя и тестовой заметки."""
        cls.user = User.objects.create_user(username='testuser')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.user
        )
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'author': cls.user,
            'slug': 'test_slug'
        }
        cls.url = reverse('notes:add')

    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку.

        Проверяет, что:
        - происходит редирект на страницу успеха
        - заметка появляется в БД
        - все атрибуты заметки соответствуют переданным данным
        - автор заметки соответствует ожидаемому
        """
        # Отправляем POST-запрос для создания заметки
        response = self.auth_client.post(self.url, data=self.form_data)

        # Проверяем редирект на страницу успеха
        self.assertRedirects(response, reverse('notes:success'))

        # Проверяем, что количество заметок увеличилось на 1
        self.assertEqual(Note.objects.count(), 2)

        # Получаем созданную заметку из БД
        new_note = Note.objects.last()

        # Проверяем атрибуты заметки
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку.

        Проверяет, что:
        - происходит редирект на страницу логина
        - заметка не создается в БД
        """
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_uniqueness_validation(self):
        """Нельзя создать заметку с неуникальным slug.

        Проверяет, что:
        - возвращается ошибка валидации для поля slug
        - количество заметок в БД не изменяется
        """
        self.form_data['slug'] = 'test-note'  # Используем существующий slug
        form = NoteForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)
        self.assertEqual(
            form.errors['slug'],
            [f'test-note{WARNING}']
        )

    def test_slug_auto_generation(self):
        """При создании заметки без slug он генерируется автоматически.

        Проверяет, что:
        - происходит редирект на страницу успеха
        - заметка создается в БД
        - slug генерируется корректно из title
        """
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(Note.objects.count(), 2)
        self.assertRedirects(response, reverse('notes:success'))


class TestNoteEditDelete(TestCase):
    # Тексты для комментариев не нужно дополнительно создавать
    # (в отличие от объектов в БД), им не нужны ссылки на self или cls,
    # поэтому их можно перечислить просто в атрибутах класса.
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text=cls.NOTE_TEXT,
            slug='test-note',
            author=cls.author
        )
        cls.form_data = {
            'title': cls.note.title,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug
        }
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку.

        Проверяет, что:
        - происходит редирект на страницу успеха
        - данные заметки обновляются в БД
        """
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_not_author_cant_edit_note(self):
        """Не-автор не может редактировать чужую заметку.

        Проверяет, что:
        - возвращается статус 404
        - данные заметки не изменяются в БД
        """
        response = self.not_author_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку.

        Проверяет, что:
        - происходит редирект на страницу успеха
        - заметка удаляется из БД
        """
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_no_author_cant_delete_note(self):
        """Не-автор не может удалить чужую заметку.

        Проверяет, что:
        - возвращается статус 404
        - заметка остается в БД
        """
        response = self.not_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
