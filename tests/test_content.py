from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .test_base import NotesTestBase

User = get_user_model()


class TestContent(NotesTestBase):
    """Тесты для проверки контента страниц приложения."""

    def test_note_in_list_for_author(self):
        """Проверка, что заметка автора присутствует в его списке заметок."""
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']

        self.assertIn(self.note, object_list)
        self.assertEqual(object_list.count(), 1)

    def test_note_not_in_list_for_another_user(self):
        """Проверка изоляции заметок пользователей."""
        response = self.reader_client.get(self.list_url)
        object_list = response.context['object_list']

        self.assertNotIn(self.note, object_list)
        self.assertEqual(object_list.count(), 0)

    def test_create_and_edit_pages_contain_form(self):
        """Проверка наличия формы на страницах создания/редактирования."""
        test_cases = (
            (self.add_url, 'form'),
            (self.edit_url, 'form'),
        )

        for url, context_key in test_cases:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn(context_key, response.context)
                self.assertIsInstance(response.context[context_key], NoteForm)
