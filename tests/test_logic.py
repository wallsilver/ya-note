from http import HTTPStatus

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import NoteForm, WARNING

User = get_user_model()


class NoteCreationTest(TestCase):
    """Тесты создания заметок (авторизованными и анонимными пользователями)."""

    # Константы для тестовых данных
    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'test-note'
    NEW_NOTE_TITLE = 'Новая заметка'
    NEW_NOTE_TEXT = 'Текст новой заметки'
    NEW_NOTE_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных перед всеми тестами класса."""
        cls.user = User.objects.create_user(username='testuser')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG
        }

    def _create_note(self):
        """Создает тестовую заметку."""
        return Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.NOTE_SLUG,
            author=self.user
        )

    def _assert_note_attributes(self, note):
        """Проверяет соответствие атрибутов заметки ожидаемым значениям."""
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_authorized_user_can_create_note(self):
        """Проверка создания заметки авторизованным пользователем."""
        initial_count = Note.objects.count()
        response = self.auth_client.post(self.url, data=self.form_data)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), initial_count + 1)

        new_note = Note.objects.last()
        self._assert_note_attributes(new_note)

    def test_anonymous_user_cant_create_note(self):
        """Проверка невозможности создания заметки анонимным пользователем."""
        initial_count = Note.objects.count()
        response = self.client.post(self.url, data=self.form_data)

        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_slug_uniqueness_validation(self):
        """Проверка валидации уникальности slug."""
        self._create_note()
        initial_count = Note.objects.count()

        self.form_data['slug'] = self.NOTE_SLUG
        form = NoteForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)
        self.assertEqual(form.errors['slug'], [f'{self.NOTE_SLUG}{WARNING}'])
        self.assertEqual(Note.objects.count(), initial_count)

    def test_slug_auto_generation(self):
        """Проверка автоматической генерации slug при его отсутствии."""
        initial_count = Note.objects.count()
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)

        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertRedirects(response, reverse('notes:success'))


class NoteEditDeleteTest(TestCase):
    """Тесты редактирования и удаления заметок."""

    # Константы для тестовых данных
    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'
    NOTE_SLUG = 'test-note'

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных перед всеми тестами класса."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_author_can_edit_note(self):
        """Проверка редактирования заметки автором."""
        response = self.author_client.post(self.edit_url, data=self.form_data)

        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_reader_cant_edit_note(self):
        """Проверка невозможности редактирования чужой заметки."""
        initial_text = self.note.text
        response = self.reader_client.post(self.edit_url, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, initial_text)

    def test_author_can_delete_note(self):
        """Проверка удаления заметки автором."""
        initial_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_reader_cant_delete_note(self):
        """Проверка невозможности удаления чужой заметки."""
        initial_count = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
