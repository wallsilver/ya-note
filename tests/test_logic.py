from django.test import TestCase
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm, WARNING

User = get_user_model()


class NoteFormTest(TestCase):
    """Тестирование формы создания и редактирования заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных: пользователя и тестовой заметки."""
        cls.author = User.objects.create_user(username='testuser')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )

    def test_slug_auto_generation(self):
        """
        Проверка автоматической генерации slug при пустом значении.

        При создании заметки с пустым slug должен автоматически
        генерироваться slug на основе заголовка.
        """
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
        """
        Проверка валидации уникальности slug.

        При попытке создать заметку с уже существующим slug
        форма должна быть невалидной и содержать ошибку.
        """
        form_data = {
            'title': 'Другая заметка',
            'text': 'Текст другой заметки',
            'slug': 'test-note'  # Используем существующий slug
        }
        form = NoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)
        self.assertEqual(
            form.errors['slug'],
            [f'test-note{WARNING}']
        )

    def test_existing_note_update(self):
        """
        Проверка обновления существующей заметки.

        При обновлении заметки с тем же slug форма должна быть валидной,
        и изменения должны сохраняться корректно.
        """
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
        """
        Проверка наличия всех полей в форме.

        Форма должна содержать все необходимые поля:
        - title
        - text
        - slug
        """
        form = NoteForm()
        self.assertIn('title', form.fields)
        self.assertIn('text', form.fields)
        self.assertIn('slug', form.fields)
