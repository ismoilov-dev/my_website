import datetime

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Blog, Certificate, FeedComment, FeedPost, Talk
from .templatetags.blog_extras import bulletize

ADMIN = '/ismatismoilov709/'


class HealthzTest(TestCase):
    def test_healthz_endpoint(self):
        response = self.client.get(reverse('healthz'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok', 'database': 'ok'})


class PublicPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = Blog.objects.create(title='Django signals', content='Words. ' * 60)

    def test_every_public_page_renders(self):
        for name in ('index', 'about', 'blogs', 'talks', 'cv', 'feed'):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_blog_index_marks_up_posts_for_the_search_filter(self):
        """main.js filters on this attribute, so it has to be lower-cased."""
        response = self.client.get(reverse('blogs'))

        self.assertContains(response, 'id="postSearch"')
        self.assertContains(response, 'data-post-title="django signals"')

    def test_article_page_offers_sharing_and_reading_progress(self):
        response = self.client.get(reverse('blog_detail', args=[self.post.pk]))

        self.assertContains(response, 'data-progress-target')
        self.assertContains(response, 'id="shareBtn"')
        self.assertContains(response, 'https://t.me/share/url')

    def test_article_navigation_links_to_neighbouring_posts(self):
        older = Blog.objects.create(title='Older post', content='Words.')
        Blog.objects.filter(pk=older.pk).update(
            created_at=self.post.created_at - datetime.timedelta(days=1)
        )

        response = self.client.get(reverse('blog_detail', args=[self.post.pk]))

        self.assertContains(response, 'Older post')

    def test_no_template_comment_leaks_into_a_page(self):
        """Django's {# #} is single-line; a multi-line one renders as text."""
        for name in ('index', 'about', 'blogs', 'talks', 'cv', 'feed'):
            with self.subTest(page=name):
                body = self.client.get(reverse(name)).content.decode()
                self.assertNotIn('{#', body)
                self.assertNotIn('{%', body)

    def test_feed_hides_unapproved_comments(self):
        post = FeedPost.objects.create(content='Hello')
        FeedComment.objects.create(post=post, author_name='Visible', content='hi')
        FeedComment.objects.create(
            post=post, author_name='Hidden', content='spam', is_approved=False
        )

        response = self.client.get(reverse('feed'))

        self.assertContains(response, 'Visible')
        self.assertNotContains(response, 'Hidden')


class BulletizeTests(TestCase):
    def test_dashed_lines_become_a_list(self):
        self.assertEqual(
            bulletize('- One\n- Two'),
            '<ul class="cv-bullets"><li>One</li><li>Two</li></ul>',
        )

    def test_double_stars_are_bold_not_bullets(self):
        self.assertEqual(bulletize('**Lead** engineer'),
                         '<p><strong>Lead</strong> engineer</p>')

    def test_admin_text_cannot_inject_markup(self):
        self.assertIn('&lt;script&gt;', bulletize('<script>alert(1)</script>'))


class BlogAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            'admin', 'admin@example.com', 'password'
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_every_changelist_and_add_form_renders(self):
        models = (
            'blog', 'feedpost', 'feedcomment', 'talk', 'workexperience',
            'project', 'education', 'certificate', 'voluntaryactivity',
        )
        for model in models:
            for view in ('', 'add/'):
                with self.subTest(model=model, view=view or 'changelist'):
                    response = self.client.get(f'{ADMIN}blog/{model}/{view}')
                    self.assertEqual(response.status_code, 200)

    def test_each_form_explains_where_the_content_appears(self):
        """The fieldset descriptions are the whole point of the rewrite."""
        for model, expected in (
            ('blog', '/blogs/'),
            ('feedpost', '/feed/'),
            ('talk', '/talks/'),
            ('project', '/cv/'),
        ):
            with self.subTest(model=model):
                response = self.client.get(f'{ADMIN}blog/{model}/add/')
                self.assertContains(response, expected)

    def test_changelist_previews_uploaded_media(self):
        Blog.objects.create(title='With cover', content='x', image='blog/cover.jpg')

        response = self.client.get(f'{ADMIN}blog/blog/')

        self.assertContains(response, 'blog/cover.jpg')

    def test_changelist_survives_records_with_no_media(self):
        Blog.objects.create(title='No cover', content='x')
        FeedPost.objects.create(content='No media')
        Certificate.objects.create(title='No proof')

        for model in ('blog/blog', 'blog/feedpost', 'blog/certificate'):
            with self.subTest(model=model):
                self.assertEqual(self.client.get(f'{ADMIN}{model}/').status_code, 200)

    def test_comment_actions_toggle_visibility_on_the_site(self):
        post = FeedPost.objects.create(content='Hello')
        comment = FeedComment.objects.create(post=post, author_name='A', content='hi')

        self.client.post(f'{ADMIN}blog/feedcomment/', {
            'action': 'hide_comments',
            '_selected_action': [str(comment.pk)],
        })
        comment.refresh_from_db()
        self.assertFalse(comment.is_approved)

        self.client.post(f'{ADMIN}blog/feedcomment/', {
            'action': 'approve_comments',
            '_selected_action': [str(comment.pk)],
        })
        comment.refresh_from_db()
        self.assertTrue(comment.is_approved)

    def test_admin_never_serves_the_dark_theme(self):
        """The panel is grey and white regardless of the operating system."""
        response = self.client.get(f'{ADMIN}blog/blog/')

        self.assertNotContains(response, 'dark_mode.css')
        self.assertContains(response, 'css/admin.css')

    def test_talk_form_warns_about_video_formats(self):
        response = self.client.get(f'{ADMIN}blog/talk/add/')

        self.assertContains(response, 'MP4')

    def test_talk_changelist_shows_whether_a_video_is_attached(self):
        Talk.objects.create(title='No video yet')

        self.assertEqual(self.client.get(f'{ADMIN}blog/talk/').status_code, 200)
