from http import HTTPStatus

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase


from posts.models import Group, Post

User = get_user_model()


class UrlsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Test',
            slug='Test',
            description='Test'
        )
        cls.post = Post.objects.create(
            text='Test',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_by_all(self):
        url_names = {
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/'
        }
        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_template(self):
        template_and_urls = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/'
        }
        for template, adress in template_and_urls.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_correct_template_by_owner(self):
        template_and_urls = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html'
        }
        for adress, template in template_and_urls.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
