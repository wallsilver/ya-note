from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import NoteForm, WARNING
from .test_base import NotesTestBase

User = get_user_model()


class NoteCreationTest(NotesTestBase):
    """Тесты создания заметок."""

    def test_author_can_create_note(self):
        """Автор может создать заметку."""
        initial_count = Note.objects.count()
        response = self.author_client.post(
            self.add_url, data=self.new_note_data
        )

        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, initial_count + 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        initial_count = Note.objects.count()
        redirect_url = f'{self.login_url}?next={self.add_url}'
        response = self.client.post(self.add_url, data=self.new_note_data)

        notes_count = Note.objects.count()
        self.assertRedirects(response, redirect_url)
        self.assertEqual(notes_count, initial_count)

    def test_slug_uniqueness_validation(self):
        """Проверка валидации уникальности slug."""
        self.new_note_data['slug'] = self.note.slug
        form = NoteForm(data=self.new_note_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['slug'],
            [f'{self.note.slug}{WARNING}']
        )

    def test_slug_auto_generation(self):
        """Проверка автоматической генерации slug."""
        self.new_note_data.pop('slug')
        response = self.author_client.post(
            self.add_url, data=self.new_note_data
        )

        new_note = Note.objects.last()
        expected_slug = slugify(self.new_note_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertRedirects(response, self.success_url)


class NoteEditDeleteTest(NotesTestBase):
    """Тесты редактирования и удаления заметок."""

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        initial_count = Note.objects.count()
        response = self.author_client.post(
            self.edit_url, data=self.new_note_data
        )

        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        note = Note.objects.get()
        self.assertEqual(note.text, self.new_note_data['text'])
        self.assertEqual(notes_count, initial_count)

    def test_reader_cant_edit_note(self):
        """Читатель не может редактировать чужую заметку."""
        initial_count = Note.objects.count()
        original_text = self.note.text
        response = self.reader_client.post(
            self.edit_url, data=self.new_note_data
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        note = Note.objects.get()
        self.assertEqual(note.text, original_text)
        self.assertEqual(notes_count, initial_count)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        initial_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)

        notes_count = Note.objects.count()
        self.assertRedirects(response, self.success_url)
        self.assertEqual(notes_count, initial_count - 1)

    def test_reader_cant_delete_note(self):
        """Читатель не может удалить чужую заметку."""
        initial_count = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)

        notes_count = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count, initial_count)
