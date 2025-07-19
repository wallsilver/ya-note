from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class NotesTestBase(TestCase):
    """Базовый класс для тестов приложения notes."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # 1. Создаем пользователей
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        # 2. Создаем и авторизуем клиентов
        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)
        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)

        # 3. Создаем тестовую заметку
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )

        # 4. Подготавливаем URL-адреса
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.home_url = reverse('notes:home')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

        cls.new_note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-slug'
        }
