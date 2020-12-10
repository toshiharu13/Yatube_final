from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
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
            text='ТестаПост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user1 = get_user_model().objects.create_user(username='Testa')
        # Создаем второй клиент
        self.authorized_client = Client()
        # создаём клиент автора поста
        self.author_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user1)
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

    def test_200_for_autorised(self):
        """Доступность url-а авторизованному пользователю"""
        templates_url_names = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': 'testtitle'}),
            reverse('new_post'),
            reverse('profile', kwargs={'username': 'Testa'}),
            reverse(
                'post', kwargs={'username': 'testa', 'post_id': self.post.id}
            ),
            reverse('about-author'),
            reverse('about-spec'),

        )

        for pages in templates_url_names:
            with self.subTest():
                response = self.authorized_client.get(pages)
                self.assertEqual(response.status_code, 200, pages)

    def test_200_for_guest(self):
        """Доступность url-а не авторизованному пользователю"""
        templates_url_names = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': 'testtitle'}),
            reverse('new_post'),

        )

        for pages in templates_url_names:
            with self.subTest():
                response = self.guest_client.get(pages)
                self.assertEqual(response.status_code, 200, pages)

    def test_urls_for_autorised(self):
        """Соответствие url-а вызванному шаблону
        для авторизованного пользователя"""
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': 'testtitle'})
            ),
        }

        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_url_for_not_author(self):
        """Соответствие url-а вызванному шаблону New для не автора"""
        templates_url_names = {
            'new.html': reverse('new_post'),
            'new.html': reverse('post_edit', kwargs={
                'username': 'testa', 'post_id': self.post.id}),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateNotUsed(response, template)

    def test_urls_for_guest(self):
        """Соответствие url-а вызванному шаблону для гостя"""
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': 'testtitle'})
            ),
        }

        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_new_for_guest(self):
        """Соответствие url-а вызванному шаблону New для гостя"""
        templates_url_names = {
            'new.html': reverse('new_post'),
            'new.html': reverse('post_edit', kwargs={
                'username': 'testa', 'post_id': self.post.id
            }),
        }

        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateNotUsed(response, template)

    def test_urls_for_author(self):
        """Соответствие url-а вызванному шаблону для автора"""
        templates_url_names = {
            'new.html': reverse('post_edit', kwargs={
                'username': 'testa', 'post_id': self.group.id
            }),
        }
        self.author_client.force_login(self.user)
        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_editpost_list_url_redirect_anonymous(self):
        """Страница /<username>/<post_id>/edit/
        перенаправляет анонимного пользователя."""
        name = reverse('post_edit', kwargs={
            'username': 'testa', 'post_id': self.group.id
        })
        response = self.guest_client.get(name)
        self.assertEqual(response.status_code, 302)

    def test_404_for_nonexistent_adress(self):
        """возврат 404 несуществующей старнице"""
        nonexistend_url = '/mikalyumba/'
        response = self.guest_client.get(nonexistend_url)
        self.assertEqual(response.status_code, 404)
