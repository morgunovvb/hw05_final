from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):

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

    def test_models_have_correct_object_names(self):
        """Проверяем, что у постов корректно работает __str__"""
        post = PostModelTest.post
        group = PostModelTest.group
        post_str_method = post.text[:15]
        group_str_method = group.title
        self.assertEqual(post_str_method, str(post))
        self.assertEqual(group_str_method, str(group))
