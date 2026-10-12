from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from ehealth_app.models import People, PeopleResearchLink


class Command(BaseCommand):
    help = 'Seed three clearly labelled demo research outputs for David Akwuru in SQLite.'

    def add_arguments(self, parser):
        parser.add_argument('--demo', action='store_true', help='Use placeholder records and example.org links.')

    @transaction.atomic
    def handle(self, *args, **options):
        if connection.vendor != 'sqlite':
            raise CommandError('Demo research outputs are restricted to SQLite. Use --test.')
        if not options['demo']:
            raise CommandError('Use --demo for placeholder data. Real outputs need verified titles and links.')
        try:
            person = People.objects.get(slug='david-001')
        except People.DoesNotExist:
            raise CommandError('David is missing. Run seed_people --test first.')
        count = 0
        for position, category in enumerate(['publication', 'poster', 'presentation']):
            _, created = PeopleResearchLink.objects.get_or_create(
                people=person, category=category,
                url=f'https://example.org/david-akwuru/demo-{category}',
                defaults={
                    'title': f'[DEMO] {category.title()} — AML data harmonisation',
                    'authors': 'David Akwuru (demo attribution)',
                    'description': 'Demo record for testing the profile layout. This is not a verified research output. Replace the title, link, and metadata with actual details.',
                    'position': position,
                },
            )
            count += int(created)
        self.stdout.write(self.style.SUCCESS(f'Created {count} demo research links for David Akwuru. Existing links were preserved.'))
