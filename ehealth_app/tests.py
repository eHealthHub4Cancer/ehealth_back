from django.test import Client, TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.management import call_command
from io import StringIO
from tempfile import TemporaryDirectory
from pathlib import Path

from .models import People, PeopleInformation, PeopleResearchLink, PeopleTitle, SocialPlatform, PeopleSocialLink


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class AdminThemeTests(TestCase):
    @override_settings(ALLOWED_HOSTS=['ehealth4cancer.org'])
    def test_login_accepts_trusted_https_origin_but_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse('admin:login'), HTTP_HOST='ehealth4cancer.org')
        self.assertEqual(response.status_code, 200)
        token = client.cookies['csrftoken'].value
        response = client.post(reverse('admin:login'), {
            'username': 'invalid-user', 'password': 'invalid-password', 'csrfmiddlewaretoken': token,
        }, HTTP_HOST='ehealth4cancer.org', HTTP_ORIGIN='https://ehealth4cancer.org')
        self.assertEqual(response.status_code, 200)
        response = client.post(reverse('admin:login'), {
            'username': 'invalid-user', 'password': 'invalid-password', 'csrfmiddlewaretoken': token,
        }, HTTP_HOST='ehealth4cancer.org', HTTP_ORIGIN='https://untrusted.example.org')
        self.assertEqual(response.status_code, 403)
        response = client.post(reverse('admin:login'), {
            'username': 'invalid-user', 'password': 'invalid-password',
        }, HTTP_HOST='ehealth4cancer.org', HTTP_ORIGIN='https://ehealth4cancer.org')
        self.assertEqual(response.status_code, 403)

    def test_admin_pages_render_with_theme_selector_and_research_inline(self):
        user = User.objects.create_superuser('theme-test', 'admin@example.org', 'test-password')
        self.client.force_login(user)
        person = People.objects.create(full_name='Theme Researcher', association='University')
        for route, args in [('admin:index', []), ('admin:ehealth_app_people_changelist', []),
                            ('admin:ehealth_app_people_change', [person.pk]),
                            ('admin:auth_user_add', [])]:
            with self.subTest(route=route):
                response = self.client.get(reverse(route, args=args))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'unfold/css/styles.css')
                self.assertContains(response, 'Dark')
                self.assertContains(response, 'Light')
                if route == 'admin:ehealth_app_people_change':
                    self.assertContains(response, 'research_links')


class SeedPeopleTests(TestCase):
    def test_complete_sample_profiles_are_repeatable_and_keep_existing_people(self):
        existing = People.objects.create(full_name='Existing Person', association='University')
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            call_command('seed_sample_people', stdout=StringIO())
            person = People.objects.get(slug='sample-amara-okafor')
            person.association = 'Edited association'
            person.save()
            call_command('seed_sample_people', stdout=StringIO())
            self.assertEqual(People.objects.filter(slug__startswith='sample-').count(), 10)
            self.assertEqual(PeopleResearchLink.objects.count(), 40)
            self.assertEqual(len(list(Path(media_root).rglob('*.png'))), 10)
            for person in People.objects.filter(slug__startswith='sample-'):
                info = PeopleInformation.objects.get(people=person)
                for field in ['research_interests', 'areas_of_expertise', 'key_initiatives',
                              'key_research_areas', 'qualifications', 'memberships', 'role_badge']:
                    self.assertTrue(getattr(info, field).exists(), field)
                self.assertEqual(person.social_links.count(), 4)
                for output in person.research_links.all():
                    for field in ['title', 'url', 'date', 'location', 'authors', 'venue', 'doi', 'description']:
                        self.assertTrue(getattr(output, field), field)
            self.assertEqual(People.objects.get(slug='sample-amara-okafor').association, 'Edited association')
            existing.refresh_from_db()
            self.assertEqual(existing.association, 'University')


    def test_david_demo_outputs_are_repeatable_and_labelled(self):
        call_command('seed_people', stdout=StringIO())
        call_command('seed_david_research', demo=True, stdout=StringIO())
        call_command('seed_david_research', demo=True, stdout=StringIO())
        david = People.objects.get(slug='david-001')
        self.assertEqual(david.research_links.count(), 3)
        self.assertEqual(set(david.research_links.values_list('category', flat=True)),
                         {'publication', 'poster', 'presentation'})
        self.assertTrue(all(link.title.startswith('[DEMO]') for link in david.research_links.all()))

    def test_seed_can_be_repeated_and_preserves_edited_profiles(self):
        call_command('seed_people', stdout=StringIO())
        self.assertEqual(People.objects.count(), 11)
        self.assertEqual(PeopleInformation.objects.count(), 11)
        profile = PeopleInformation.objects.first()
        profile.about_user = 'Edited biography'
        profile.save()
        call_command('seed_people', stdout=StringIO())
        self.assertEqual(People.objects.count(), 11)
        self.assertEqual(PeopleInformation.objects.count(), 11)
        profile.refresh_from_db()
        self.assertEqual(profile.about_user, 'Edited biography')


class PeopleResearchLinkTests(TestCase):
    def setUp(self):
        self.person = People.objects.create(full_name='Test Researcher', association='University')
        PeopleInformation.objects.create(people=self.person, about_user='Research biography')

    def test_links_available_on_all_people_endpoints_in_display_order(self):
        for position, category in enumerate(PeopleResearchLink.Category.values):
            PeopleResearchLink.objects.create(
                people=self.person, title=category.title(), category=category,
                url=f'https://example.org/{category}', position=3 - position,
            )
        other = People.objects.create(full_name='Other Researcher', association='University')
        PeopleResearchLink.objects.create(people=other, title='Unrelated', url='https://example.org/other')
        for route, kwargs in [('people-list', {}), ('people-information-all', {}),
                              ('people-information', {'slug': self.person.slug})]:
            with self.subTest(route=route):
                response = self.client.get(reverse(route, kwargs=kwargs))
                self.assertEqual(response.status_code, 200)
                data = response.json()
                profile = next(item for item in data if item['slug'] == self.person.slug) if isinstance(data, list) else data
                self.assertEqual([link['category'] for link in profile['research_links']],
                                 ['other', 'presentation', 'poster', 'publication'])
                self.assertEqual(profile['research_links'][0]['url'], 'https://example.org/other')
                self.assertNotIn('Unrelated', [link['title'] for link in profile['research_links']])

    def test_production_api_hostname_is_allowed(self):
        response = self.client.get(reverse('people-list'), HTTP_HOST='api.ehealth4cancer.eu')
        self.assertEqual(response.status_code, 200)

    def test_social_link_icon_is_in_profile_api(self):
        platform = SocialPlatform.objects.create(name='LinkedIn', icon='linkedin')
        PeopleSocialLink.objects.create(people=self.person, platform=platform, url='https://www.linkedin.com/in/example/')
        response = self.client.get(reverse('people-information', kwargs={'slug': self.person.slug}))
        self.assertEqual(response.json()['social_links'][0]['icon'], 'linkedin')

    def test_person_without_links_returns_empty_list(self):
        response = self.client.get(reverse('people-information', kwargs={'slug': self.person.slug}))
        self.assertEqual(response.json()['research_links'], [])

    def test_custom_title_and_poster_metadata_are_exposed(self):
        self.person.title = PeopleTitle.objects.create(name='Visiting Prof.')
        self.person.save()
        PeopleResearchLink.objects.create(
            people=self.person, title='Cancer Research Poster', category='poster',
            url='https://example.org/poster', date='2026-10-12', location='Dublin',
            authors='Researcher A; Researcher B', venue='Research Conference',
            doi='10.1234/example', description='Poster abstract',
        )
        response = self.client.get(reverse('people-list'))
        self.assertEqual(response.json()[0]['title'], 'Visiting Prof.')
        self.assertEqual(response.json()[0]['full_title_name'], 'Visiting Prof. Test Researcher')
        response = self.client.get(reverse('people-information', kwargs={'slug': self.person.slug}))
        self.assertEqual(response.json()['full_name'], 'Visiting Prof. Test Researcher')
        link = response.json()['research_links'][0]
        self.assertEqual(link['date'], '2026-10-12')
        self.assertEqual(link['location'], 'Dublin')
        self.assertEqual(link['authors'], 'Researcher A; Researcher B')
        self.assertEqual(link['venue'], 'Research Conference')
        self.assertEqual(link['doi'], '10.1234/example')
        self.assertEqual(link['description'], 'Poster abstract')

    def test_deleting_person_removes_research_links(self):
        link = PeopleResearchLink.objects.create(people=self.person, title='Poster', url='https://example.org/poster')
        self.person.delete()
        self.assertFalse(PeopleResearchLink.objects.filter(pk=link.pk).exists())
