from django.test import TestCase

from posts.models import Group, Post, User


class TaskModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            username='testa',
            email='testa@gmail.com',
            password='12345678',
        )

        cls.group = Group.objects.create(
            title='testtitle',
            slug='testtitle',
        )

        cls.post = Post.objects.create(
            text='Заголовок тестового поста',
            author=TaskModelTest.user,
            group=TaskModelTest.group,

        )

        # remove requests to DB, take data from created objects

    def test_title_label(self):
        """verbose_name поля text поста не должны быть пустыми."""
        verbose = self.post._meta.get_field('text').verbose_name
        self.assertIsNotNone(verbose, 'Имя поля не должно быть пустым')

    def test_title_help_text(self):
        """help_text поля text поста не должны быть пустыми."""
        help_texts = self.post._meta.get_field('text').help_text
        self.assertIsNotNone(help_texts, 'Подсказка не должна быть пустой')

    def test_group_label(self):
        """verbose_name поля tittle  группы не должны быть пустыми."""
        verbose = self.group._meta.get_field('title').verbose_name
        self.assertIsNotNone(verbose, 'Имя поля не должно быть пустым')

    def test_group_help_text(self):
        """help_text поля tittle  группы не должны быть пустыми."""
        help_texts = self.group._meta.get_field('title').help_text
        self.assertIsNotNone(help_texts, 'Подсказка не должна быть пустой')

    def test_object_name_is_text_field_post(self):
        """__str__  Post - это строчка с содержимым Post.text."""
        expected_object_name = self.post.text
        self.assertEquals(expected_object_name[:15], str(self.post),
                          'объект Post не эдентичен полю текста[:15]')

    def test_object_name_is_title_filed_group(self):
        """__str__  Group - это строчка с содержимым group.title"""
        expected_object_name = self.group.title
        self.assertEquals(expected_object_name, str(self.group),
                          'объект Group не эдентичен полю title')
