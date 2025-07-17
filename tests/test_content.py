from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class NotesTestBase(TestCase):
    """Базовый класс для тестов приложения notes."""

    @classmethod
    def setUpTestData(cls):
        # Создаем пользователей
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        # Создаем тестовую заметку
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )

        # Предварительно создаем все URL
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')


class TestContent(NotesTestBase):
    """Тесты для проверки контента страниц приложения."""

    def setUp(self):
        # Авторизуем автора перед выполнением каждого теста
        self.client.force_login(self.author)

    def test_note_in_list_for_author(self):
        """Проверка, что заметка автора присутствует в его списке заметок."""
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']

        self.assertIn(self.note, object_list)
        self.assertEqual(object_list.count(), 1)

        # Проверяем все данные заметки
        note_from_context = object_list[0]
        self.assertEqual(note_from_context.title, self.note.title)
        self.assertEqual(note_from_context.text, self.note.text)
        self.assertEqual(note_from_context.slug, self.note.slug)
        self.assertEqual(note_from_context.author, self.note.author)

    def test_note_not_in_list_for_another_user(self):
        """Проверка изоляции заметок пользователей."""
        # Переключаемся на читателя
        self.client.force_login(self.reader)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']

        self.assertNotIn(self.note, object_list)
        self.assertEqual(object_list.count(), 0)

    def test_create_and_edit_pages_contain_form(self):
        """Проверка наличия формы на страницах создания/редактирования."""
        test_cases = (
            (self.add_url, NoteForm),
            (self.edit_url, NoteForm),
        )

        for url, form_class in test_cases:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], form_class)
