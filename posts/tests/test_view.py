from django.contrib.auth import get_user_model
from django.test import Client, TestCase, modify_settings
from django.urls import reverse
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django import forms
from django.core.cache import cache

from posts.models import Post, Group, User, Follow, Comment



class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create user testa
        cls.user = User.objects.create(
            username='testa',
            email='testa@gmail.com',
            password='12345678',
        )
        # create group
        cls.group = Group.objects.create(
            title='testtitle',
            slug='testtitle',
        )
        # create sign in DB
        Post.objects.create(
            text='ТестаПост',
            author=TaskPagesTests.user,
            group=TaskPagesTests.group,
        )

    def setUp(self):
        # cache.clear()
        # create authorised client
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@gmail.com',
            password='12345678',
        )
        self.authorized_client = Client()
        self.guest_client = Client()
        # use user for authorize&make posts
        self.authorized_client.force_login(TaskPagesTests.user)
        self.testpost = Post.objects.get(text='ТестаПост')
        # create site for flatpages
        site1 = Site(pk=1, domain='localhost:8000', name='localhost:8000')
        site1.save()
        FlatPage.objects.create(
            url='/about-author/',
            title='О авторе',
            content='немного о себе',
        ).sites.add(site1)
        FlatPage.objects.create(
            url='/about-spec/',
            title='О технологии',
            content='немного о технологии',
        ).sites.add(site1)
        self.static_pages = ('/about-author/', '/about-spec/')

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # selecting " name_of_html_template: url_revers_name"
        templates_pages_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': 'testtitle'})),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        # get fields in context
        field_text = response.context.get('posts')[0].text
        field_pub_date = response.context.get('posts')[0].pub_date
        field_author = response.context.get('posts')[0].author.username
        field_group = response.context.get('posts')[0].group.title
        pubdate = self.testpost.pub_date
        # checking fields for equal
        self.assertEqual(field_text, 'ТестаПост')
        self.assertEqual(field_author, 'testa')
        self.assertEqual(field_pub_date, pubdate)
        self.assertEqual(field_group, 'testtitle')

    def test_home_page_show_correct_paginator(self):
        """В шаблон index передан корректное количесство постов на страницу."""
        response = self.authorized_client.get(reverse('index'))
        # get fields in context
        field_pages = response.context.get('page')
        # checking fields for equal
        self.assertEqual(len(field_pages), 1)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'testtitle'})
        )
        # get fields in context
        field_text = response.context.get('posts')[0].text
        field_pub_date = response.context.get('posts')[0].pub_date
        field_author = response.context.get('posts')[0].author.username
        field_group = response.context.get('posts')[0].group.title
        pubdate = self.testpost.pub_date
        # checking fields for equal
        self.assertEqual(field_text, 'ТестаПост')
        self.assertEqual(field_author, 'testa')
        self.assertEqual(field_pub_date, pubdate)
        self.assertEqual(field_group, 'testtitle')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': 'testa'})
        )
        # get fields in context
        field_text = response.context.get('post')[0].text
        field_pub_date = response.context.get('post')[0].pub_date
        field_author = response.context.get('post')[0].author.username
        pubdate = self.testpost.pub_date
        # checking fields for equal
        self.assertEqual(field_text, 'ТестаПост')
        self.assertEqual(field_author, 'testa')
        self.assertEqual(field_pub_date, pubdate)

    def test_author_post_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        postid = self.testpost.id
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': 'testa', 'post_id': postid})
        )
        # get fields in context
        field_text = response.context.get('post').text
        field_author = response.context.get('post_author').username
        field_post_id = response.context.get('post_id')
        # checking fields for equal
        self.assertEqual(field_text, 'ТестаПост')
        self.assertEqual(field_author, 'testa')
        self.assertEqual(field_post_id, postid)

        # checking context of new post(have form)
    def test_new_page_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        # list awaiting types fields of form:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        # checking, that types fields of form in context
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # checking, that field of form is instance of our class
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон new(edit) сформирован с правильным контекстом."""
        postid = self.testpost.id
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': 'testa', 'post_id': postid})
        )
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # checking, that field of form is instance of our class
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        post_text_0 = response.context.get('posts')[0].text
        post_group_0 = response.context.get('posts')[0].group.title
        self.assertEqual(post_text_0, 'ТестаПост')
        self.assertEqual(post_group_0, 'testtitle')

    def test_group_posts_pages_show_correct_context(self):
        """Шаблон group.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'testtitle'})
        )
        group_post_0 = response.context.get('posts')[0].text
        group_group_0 = response.context.get('posts')[0].group.title
        self.assertEqual(group_post_0, 'ТестаПост')
        self.assertEqual(group_group_0, str(TaskPagesTests.group))

    def test_about_author_flatpage(self):
        """Тест доступности страницы 'об авторе'"""
        response = self.guest_client.get(reverse('about-author'))
        self.assertEqual(response.status_code, 200, f'{response}')

    def test_about_spec_flatpage(self):
        """Тест доступности страницы 'о технологиях'"""
        response = self.guest_client.get(reverse('about-spec'))
        self.assertEqual(response.status_code, 200, f'{response}')

    def test_home_page_show_correct_context_with_cache(self):
        """изменение отображение контекста при работе с кэшем."""
        # get fields in context
        client = self.authorized_client
        response = client.get(reverse('index'))
        content = response.content
        # checking fields for equal
        self.assertEqual(response.content, content)
        # deleting all
        Post.objects.all().delete()
        # checking fields for equal (cache is working)
        response = client.get(reverse('index'))
        self.assertEqual(response.content, content)
        # cache.clear
        cache.clear()
        # checking fields for not equal (cache is clearing)
        response = client.get(reverse('index'))
        self.assertNotEqual(response.content, content)

    def test_follow_author(self):
        """проверка включения подписки авторизованным пользователем"""
        # create new following
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': 'testa'})
        )
        # checking for a new data in Follow model
        folowing_author = Follow.objects.filter(
            author__username='testa').exists()
        self.assertTrue(folowing_author)

    def test_unfollow_outhor(self):
        """проверка отписки авторизованного пользователя"""
        # create new following
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': 'testa'})
        )
        # checking for a new data in Follow model
        following_author = Follow.objects.filter(
            author__username='testa').exists()
        self.assertTrue(following_author)
        # delete following
        self.authorized_client.get(reverse(
            'profile_unfollow', kwargs={'username': 'testa'}))
        # checking for a result
        unfollowing_author = Follow.objects.filter(
            author__username='testa').exists()
        self.assertFalse(unfollowing_author)
        pass

    def test_new_post_in_follower_list(self):
        """после добавления подписки, посты автора появятся в ленте"""
        # making response to follow_index
        response = self.authorized_client.get(reverse('follow_index'))
        content = response.content
        # create new follow
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': 'testa'})
        )
        # check for update in content
        cache.clear()
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertNotEqual(response.content, content,
                            'Ошибка отображения, контент должен изменится')
        # check for present of post of author
        text_upd_post = response.context.get('page')[0].text
        self.assertEqual(text_upd_post, 'ТестаПост',
                         f'Ошибка отображения,{text_upd_post} должен появится')


    def test_make_comments_authorized(self):
        """Только авторизированный пользователь может комментировать посты"""
        comments_count = Comment.objects.count()
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': self.user, 'post_id': self.testpost.id}))
        form_data = {'text': 'тестатест'}


        pass



