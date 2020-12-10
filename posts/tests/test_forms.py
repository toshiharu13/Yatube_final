import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username='testa')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # create group
        cls.group = Group.objects.create(
            title='testtitle',
            slug='testtitle',
            description='test_sign'
        )
        cls.post = Post.objects.create(
            text='Test',
            author=cls.user,
        )
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    def setUp(self):
        super().setUp()
        self.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """после создания поста количество записей увеличилось,
         записанный пост соответствует переданному"""
        post_count = Post.objects.count()

        form_data = {
            'text': 'test_text',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])

    def test_edit_post(self):
        """после редактирования поста запись изменилась."""
        post = Post.objects.create(
            text='Test',
            author=self.user,
        )

        form_data = {
            'group': '',
            'text': 'Test_new',
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                        'username': self.user.username,
                        'post_id': post.id
                    }), data=form_data, follow=True
        )
        self.assertEqual(200, response.status_code)
        self.assertRedirects(response, reverse('post', kwargs={
            'username': self.user.username, 'post_id': post.id
        }))
        # get object post instead of 'get'
        post.refresh_from_db()
        self.assertEqual(post.text, form_data['text'])

    def test_new_post_creates_post_with_image(self):
        """провекрка создания поста с изображением"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test post with images.',
            'group': self.group.id,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
