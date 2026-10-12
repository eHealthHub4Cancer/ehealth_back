import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils.html import format_html_join

from ehealth_app.models import (
    People, PeopleInformation, Tag, ResearchInterest, SocialPlatform,
    PeopleSocialLink, AreaOfExpertise, KeyResearchArea, KeyInitiatives,
    Qualification, Membership, roleBadge, PeopleTitle,
)


class Command(BaseCommand):
    help = 'Import saved site people and profiles into the local SQLite database without replacing existing profiles.'

    @transaction.atomic
    def handle(self, *args, **options):
        if connection.vendor != 'sqlite' or not getattr(settings, 'DATABASES', {})['default']['NAME']:
            raise CommandError('This seed command is for SQLite only. Run it with --test.')
        source = Path(__file__).resolve().parents[2] / 'fixtures' / 'people_profiles.json'
        created_count = 0
        for entry in json.loads(source.read_text()):
            name = entry['name']
            title = ''
            for prefix, value in [('Prof ', 'Prof.'), ('Dr ', 'Dr.')]:
                if name.startswith(prefix):
                    title, name = value, name[len(prefix):]
                    break
            person, created = People.objects.get_or_create(
                slug=entry['slug'],
                defaults={'full_name': name, 'title': PeopleTitle.objects.get_or_create(name=title)[0] if title else None, 'association': entry['title']},
            )
            created_count += int(created)
            profile = entry['profile']
            info, profile_created = PeopleInformation.objects.get_or_create(
                people=person,
                defaults={
                    'about_user': str(format_html_join('', '<p>{}</p>', ((p,) for p in profile.get('bio', [])))),
                    'institution': profile.get('institution', {}).get('location', ''),
                },
            )
            if not profile_created:
                continue
            person.tags.add(*(Tag.objects.get_or_create(name=name)[0] for name in entry.get('tags', [])))
            for field, model, key, values in [
                ('research_interests', ResearchInterest, 'name', profile.get('research_interests', [])),
                ('role_badge', roleBadge, 'name', profile.get('role_badges', [])),
                ('areas_of_expertise', AreaOfExpertise, 'name', profile.get('expertise', [])),
                ('qualifications', Qualification, 'title', profile.get('qualifications', [])),
                ('memberships', Membership, 'title', profile.get('memberships', [])),
            ]:
                getattr(info, field).add(*(model.objects.get_or_create(**{key: value})[0] for value in values))
            for area in profile.get('research_areas', []):
                info.key_research_areas.add(KeyResearchArea.objects.get_or_create(
                    title=area['title'], defaults={'description': area.get('description', '')},
                )[0])
            for initiative in profile.get('key_initiatives', []):
                info.key_initiatives.add(KeyInitiatives.objects.get_or_create(
                    title=initiative['title'], url=initiative['link'],
                )[0])
            links = list(profile.get('social_links', []))
            for name, key in [('Homepage', 'homepage_url'), ('Email', 'email')]:
                if profile.get(key):
                    links.append({'name': name, 'url': profile[key]})
            for link in links:
                platform, _ = SocialPlatform.objects.get_or_create(name=link['name'])
                PeopleSocialLink.objects.get_or_create(people=person, platform=platform, url=link['url'])
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} people. Existing profiles were preserved.'))
