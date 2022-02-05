import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):

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
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            image=cls.uploaded,
            author=cls.user,
            group=cls.group,
        )
        cls.comments = Comment.objects.create(
            post=cls.post,
            text='Тестовый комм',
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower = User.objects.create_user(username='follower')

    def test_follow(self):
        follow_count = Follow.objects.count()
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': self.follower}
        ))
        self.assertIs(
            Follow.objects.filter(
                user=self.user, author=self.follower
            ).exists(),
            True
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollow(self):
        Follow.objects.create(user=self.user, author=self.follower)
        self.authorized_client.post(reverse(
            'posts:profile_unfollow', kwargs={'username': self.follower}
        ))
        self.assertIs(
            Follow.objects.filter(
                user=self.user, author=self.follower
            ).exists(),
            False
        )

    def test_new_post_in_favourites(self):
        Follow.objects.get_or_create(user=self.user, author=self.follower)
        follow_post = Post.objects.create(author=self.follower)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(follow_post, response.context['page_obj'])
        self.authorized_client.logout()
        User.objects.create_user(username='NewUser', password='New12345')
        self.client.login(username='NewUser', password='New12345')
        response = self.client.get(reverse('posts:follow_index'))
        self.assertNotIn(follow_post, response.context['page_obj'])
