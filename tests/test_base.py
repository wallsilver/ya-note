from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

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