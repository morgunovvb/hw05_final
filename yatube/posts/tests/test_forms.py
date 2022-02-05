import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Test',
            slug='Test',
            description='Test'
        )
        cls.post = Post.objects.create(
            text='Test',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        data = {
            'text': 'Hello',
            'group': self.group.id,
            'image': self.post.image,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True
        )
        post = Post.objects.all().latest('id')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(data['text'], post.text)
        self.assertEqual(data['group'], post.group.id)
        self.assertEqual(
            data['image'].name, self.post.image.name
        )

    def test_edit_post(self):
        posts_count = Post.objects.count()
        data = {
            'text': 'hi',
            'group': self.group.id,
            'image': self.post.image,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=data,
            follow=True
        )
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(data['text'], post.text)
        self.assertEqual(data['group'], post.group.id)
        self.assertEqual(
            data['image'].name, self.post.image.name
        )
