from django.test import TestCase
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm, WARNING

User = get_user_model()


class NoteFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='testuser')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )

    def test_slug_auto_generation(self):
        """Тест автоматической генерации slug при пустом значении."""
        form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': ''
        }
        form = NoteForm(data=form_data)
        self.assertTrue(form.is_valid())
        note = form.save(commit=False)
        note.author = self.author
        note.save()
        self.assertTrue(note.slug.startswith('novaya-zametka'))

    def test_slug_uniqueness_validation(self):
        """Тест валидации уникальности slug."""
        form_data = {
            'title': 'Другая заметка',
            'text': 'Текст другой заметки',
            'slug': 'test-note'  # Используем существующий slug
        }
        form = NoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)
        self.assertEqual(form.errors['slug'], [f'test-note{WARNING}'])

    def test_existing_note_update(self):
        """Тест обновления существующей заметки с тем же slug."""
        form_data = {
            'title': 'Обновленная заметка',
            'text': 'Обновленный текст',
            'slug': 'test-note'
        }
        form = NoteForm(data=form_data, instance=self.note)
        self.assertTrue(form.is_valid())
        form.save()
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Обновленная заметка')

    def test_form_fields(self):
        """Тест наличия всех полей в форме."""
        form = NoteForm()
        self.assertIn('title', form.fields)
        self.assertIn('text', form.fields)
        self.assertIn('slug', form.fields)
