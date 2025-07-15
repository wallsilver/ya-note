from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Тесты для проверки контента страниц приложения."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных для всех методов тестирования."""
        # Создаём двух пользователей.
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        # Создаём заметку от имени автора.
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_note_in_list_for_author(self):
        """Проверка, что заметка автора присутствует в его списке заметок.

        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        """Проверка изоляции заметок пользователей.

        В список заметок одного пользователя не попадают
        заметки другого пользователя.
        """
        self.client.force_login(self.reader)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_and_edit_pages_contain_form(self):
        """Проверка наличия формы на страницах создания и редактирования.

        На страницы создания и редактирования заметки передаются формы.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
