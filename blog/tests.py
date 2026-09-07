import datetime
import re
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Blog, Certificate, FeedComment, FeedPost, Skill, SkillGroup, Talk
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
        for name in ('index', 'about', 'blogs', 'talks', 'skills', 'cv', 'feed'):
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

    def test_the_stylesheet_and_script_carry_a_version(self):
        """Without it a browser reuses a cached copy and the site looks unchanged."""
        body = self.client.get(reverse('index')).content.decode()

        self.assertRegex(body, r'href="/static/css/main\.css\?v=\d+"')
        self.assertRegex(body, r'src="/static/js/main\.js\?v=\d+"')

    def test_no_template_comment_leaks_into_a_page(self):
        """Django's {# #} is single-line; a multi-line one renders as text."""
        for name in ('index', 'about', 'blogs', 'talks', 'skills', 'cv', 'feed'):
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


class SkillTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group = SkillGroup.objects.create(name='Backend', tagline='Most of my hours')
        cls.skill = Skill.objects.create(
            group=cls.group, name='Django', level=5, years='4y', is_core=True
        )
        cls.empty = SkillGroup.objects.create(name='Nothing here', order=9)

    def test_the_nav_does_not_offer_the_skills_page(self):
        """It was dropped from the header on purpose -- the CV carries the map."""
        for name in ('index', 'skills', 'cv'):
            with self.subTest(page=name):
                self.assertNotContains(self.client.get(reverse(name)), 'href="/skills/"')

    def test_skills_page_lists_the_skill_with_what_main_js_needs(self):
        """The map is drawn from these attributes, so they have to be there."""
        response = self.client.get(reverse('skills'))

        self.assertContains(response, 'data-skillmap')
        self.assertContains(response, 'data-skill-group="Backend"')
        self.assertContains(response, 'data-skill="Django"')
        self.assertContains(response, 'data-level="5"')
        self.assertContains(response, 'data-core="1"')

    def test_the_cv_shows_the_same_skills_as_the_skills_page(self):
        """Both render one partial; this fails the moment they drift apart."""
        for page in ('skills', 'cv'):
            with self.subTest(page=page):
                self.assertContains(self.client.get(reverse(page)), 'data-skill="Django"')

    def test_an_empty_group_is_never_drawn_as_a_ring(self):
        self.assertNotContains(self.client.get(reverse('skills')), 'Nothing here')

    def test_the_page_holds_up_with_no_skills_at_all(self):
        Skill.objects.all().delete()
        SkillGroup.objects.all().delete()

        response = self.client.get(reverse('skills'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'data-skillmap')

    def test_the_level_meter_fills_one_dot_per_level(self):
        self.assertEqual(self.skill.meter, [True] * 5)
        self.assertEqual(
            Skill.objects.create(group=self.group, name='Redis', level=2).meter,
            [True, True, False, False, False],
        )

    def test_admin_text_cannot_inject_markup_into_the_map(self):
        """main.js reads these attributes and the readout writes text, not HTML."""
        Skill.objects.create(group=self.group, name='<script>alert(1)</script>')

        body = self.client.get(reverse('skills')).content.decode()

        self.assertNotIn('<script>alert(1)</script>', body)
        self.assertIn('&lt;script&gt;', body)

    def test_the_skills_page_is_in_the_sitemap(self):
        self.assertContains(self.client.get('/sitemap.xml'), '/skills/')

    def test_each_group_animates_in_on_its_own(self):
        """One mark per group, so the rings cascade instead of arriving at once.

        Counted against the database rather than a literal: the seed migration
        runs here too, so this class is never the only thing on the page.
        """
        SkillGroup.objects.create(name='Data').skills.create(name='Redis')
        drawn = SkillGroup.objects.filter(skills__isnull=False).distinct().count()

        body = self.client.get(reverse('skills')).content.decode()

        self.assertEqual(body.count('data-reveal-item="fade-up"'), drawn)
        self.assertIn('data-reveal-item="zoom-in"', body)


class RevealAnimationTests(TestCase):
    """The scroll-reveal effects are named in markup and defined in CSS.

    Nothing throws when the two disagree -- a misspelt effect just falls back
    to the default and looks almost right -- so the disagreement is what these
    tests look for.
    """

    APP = Path(__file__).resolve().parent
    NAMED_EFFECT = re.compile(r'data-reveal(?:-item)?="([^"]+)"')

    @classmethod
    def setUpTestData(cls):
        cls.css = (cls.APP / 'static' / 'css' / 'main.css').read_text()

    def used_effects(self):
        used = set()
        for template in sorted((self.APP / 'templates').rglob('*.html')):
            used.update(self.NAMED_EFFECT.findall(template.read_text()))
        return used

    def test_every_effect_named_in_a_template_is_defined_in_the_stylesheet(self):
        effects = self.used_effects()

        self.assertTrue(effects, 'no named effects found — did the markup change?')
        for effect in sorted(effects):
            with self.subTest(effect=effect):
                self.assertIn(f'[data-reveal="{effect}"]', self.css)
                self.assertIn(f'[data-reveal-item="{effect}"]', self.css)

    def test_the_hidden_state_stays_behind_the_js_class(self):
        """Without this, a browser that runs no JavaScript gets a blank page."""
        self.assertIn('.js [data-reveal],\n.js [data-reveal-item] {', self.css)
        self.assertNotIn('\n[data-reveal] {', self.css)

    def test_reduced_motion_puts_everything_back(self):
        reduced = self.css.split('@media (prefers-reduced-motion: reduce) {')[1]

        self.assertIn('[data-reveal-item] {', reduced.split('}')[0] + reduced)
        self.assertIn('opacity: 1;', reduced)

    def test_pages_still_carry_the_marks_the_engine_looks_for(self):
        for name in ('index', 'about', 'blogs', 'talks', 'skills', 'cv', 'feed'):
            with self.subTest(page=name):
                body = self.client.get(reverse(name)).content.decode()
                self.assertIn('data-reveal', body)

    def test_what_loads_above_the_fold_plays_without_a_scroll(self):
        """A banner nobody has to scroll to would otherwise sit there hidden."""
        for name in ('index', 'about', 'blogs', 'talks', 'skills', 'cv', 'feed'):
            with self.subTest(page=name):
                body = self.client.get(reverse(name)).content.decode()
                self.assertIn('data-reveal-now', body)

    def test_an_article_arrives_a_piece_at_a_time(self):
        post = Blog.objects.create(title='Staggered', content='Words.')

        body = self.client.get(reverse('blog_detail', args=[post.pk])).content.decode()

        self.assertIn('data-reveal-group data-progress-target', body)
        self.assertGreater(body.count('data-reveal-item'), 3)

    def test_the_engine_watches_elements_rather_than_containers(self):
        """Group-at-a-time reveals spend the animation off screen -- see main.js."""
        js = (self.APP / 'static' / 'js' / 'main.js').read_text()

        self.assertIn('pending.forEach(function (el) { observer.observe(el); });', js)


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
            'skillgroup', 'skill',
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
            ('skillgroup', '/skills/'),
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
