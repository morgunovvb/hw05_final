from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

from yatube.settings import PAGINATOR_CONST

User = get_user_model()


class ViewsTests(TestCase):

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
            image=cls.uploaded,
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def check_context(self, response):
        self.response = response
        response_id = response.context['page_obj'][0].id
        response_text = response.context['page_obj'][0].text
        response_author = response.context['page_obj'][0].author
        response_group = response.context['page_obj'][0].group
        response_image = response.context['page_obj'][0].image
        self.assertEqual(response_id, self.post.id)
        self.assertEqual(response_text, self.post.text)
        self.assertEqual(response_author, self.user)
        self.assertEqual(response_group, self.group)
        self.assertEqual(response_image, self.post.image)

    def test_index_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_context(response)

    def test_group_list_context(self):
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': self.group.slug})
        )
        self.check_context(response)

    def test_profile_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.check_context(response)

    def test_post_detail(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context['posts'].author, self.user)
        self.assertEqual(response.context['posts'].text, self.post.text)
        self.assertEqual(response.context['posts'].image, self.post.image)

    def test_create_post(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        text_initial = response.context['form'].fields['text'].initial
        group_initial = response.context['form'].fields['group'].initial
        self.assertEqual(group_initial, None)
        self.assertEqual(text_initial, None)

    def test_edit_post(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}
        ))
        text_initial = response.context['form'].fields['text'].initial
        group_initial = response.context['form'].fields['group'].initial
        self.assertEqual(group_initial, None)
        self.assertEqual(text_initial, None)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description',
        )

    def setUp(self):
        self.count_posts = 13
        for post_on_page in range(self.count_posts):
            self.post = Post.objects.create(
                text='Тестовый текст %s' % post_on_page,
                author=self.user,
                group=self.group,
            )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_first_index_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), PAGINATOR_CONST)

    def test_second_index_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj']), (self.count_posts % PAGINATOR_CONST)
        )

    def test_first_group_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), PAGINATOR_CONST)

    def test_second_group_contains_three_records(self):
        response = self.authorized_client.get(reverse(
            'posts:group', kwargs={'slug': self.group.slug}
        ) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), (self.count_posts % PAGINATOR_CONST)
        )

    def test_first_profile_contains_ten_records(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}
        ))
        self.assertEqual(len(response.context['page_obj']), PAGINATOR_CONST)

    def test_second_profile_contains_three_records(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}
        ) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), (self.count_posts % PAGINATOR_CONST)
        )
